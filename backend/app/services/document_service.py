from fastapi import HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.document import Document, DocumentStatus
from app.models.user import User
from app.services.parser_service import extract_text_from_file
from app.services.storage_service import storage_service
from app.utils.file_utils import is_allowed_file


async def create_document(db: Session, owner: User, file: UploadFile) -> Document:
    if not file.filename:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Missing filename")

    if not is_allowed_file(file.filename, file.content_type):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF, DOCX, CSV, and TXT files are supported",
        )

    stored_filename, storage_path, size = await storage_service.save_upload(file, owner.id)
    max_bytes = settings.MAX_UPLOAD_MB * 1024 * 1024
    if size > max_bytes:
        storage_service.delete(storage_path)
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File exceeds {settings.MAX_UPLOAD_MB} MB upload limit",
        )

    document = Document(
        owner_id=owner.id,
        original_filename=file.filename,
        stored_filename=stored_filename,
        storage_path=storage_path,
        content_type=file.content_type or "application/octet-stream",
        file_size=size,
        status=DocumentStatus.UPLOADED,
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    process_document_text(db, document)
    return document


def process_document_text(db: Session, document: Document) -> None:
    document.status = DocumentStatus.PROCESSING
    db.commit()
    try:
        extracted_text = extract_text_from_file(document.storage_path, document.content_type)
        document.extracted_text = extracted_text
        document.status = DocumentStatus.PROCESSED if extracted_text else DocumentStatus.UPLOADED
        document.error_message = None if extracted_text else "Text extraction will run in the parser milestone"
    except Exception as exc:
        document.status = DocumentStatus.FAILED
        document.error_message = str(exc)
    db.commit()
    db.refresh(document)


def list_documents(db: Session, owner: User) -> list[Document]:
    return (
        db.query(Document)
        .filter(Document.owner_id == owner.id)
        .order_by(Document.created_at.desc())
        .all()
    )


def get_owned_document(db: Session, owner: User, document_id: int) -> Document:
    document = (
        db.query(Document)
        .filter(Document.id == document_id, Document.owner_id == owner.id)
        .first()
    )
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


def delete_document(db: Session, owner: User, document_id: int) -> None:
    document = get_owned_document(db, owner, document_id)
    storage_path = document.storage_path
    db.delete(document)
    db.commit()
    storage_service.delete(storage_path)


def update_document(db: Session, owner: User, document_id: int, original_filename: str) -> Document:
    cleaned_name = original_filename.strip()
    if not cleaned_name:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Document name cannot be empty")

    document = get_owned_document(db, owner, document_id)
    document.original_filename = cleaned_name
    db.commit()
    db.refresh(document)
    return document
