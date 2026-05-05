from datetime import datetime

from pydantic import BaseModel

from app.models.document import DocumentStatus


class DocumentRead(BaseModel):
    id: int
    original_filename: str
    content_type: str
    file_size: int
    status: DocumentStatus
    error_message: str | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class DocumentDetail(DocumentRead):
    extracted_text_preview: str | None = None


class DocumentUploadResponse(BaseModel):
    document: DocumentRead
    message: str


class DocumentUpdate(BaseModel):
    original_filename: str
