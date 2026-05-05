from fastapi import APIRouter, Depends, File, UploadFile, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.document import DocumentDetail, DocumentRead, DocumentUpdate, DocumentUploadResponse
from app.services.document_service import (
    create_document,
    delete_document,
    get_owned_document,
    list_documents,
    update_document,
)


router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentUploadResponse:
    document = await create_document(db, current_user, file)
    return DocumentUploadResponse(document=document, message="Document uploaded successfully")


@router.get("", response_model=list[DocumentRead])
def read_documents(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> list[DocumentRead]:
    return list_documents(db, current_user)


@router.get("/{document_id}", response_model=DocumentDetail)
def read_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentDetail:
    document = get_owned_document(db, current_user, document_id)
    preview = document.extracted_text[:1200] if document.extracted_text else None
    return DocumentDetail.model_validate(document).model_copy(update={"extracted_text_preview": preview})


@router.patch("/{document_id}", response_model=DocumentRead)
def rename_document(
    document_id: int,
    payload: DocumentUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> DocumentRead:
    return update_document(db, current_user, document_id, payload.original_filename)


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_document(
    document_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> None:
    delete_document(db, current_user, document_id)
