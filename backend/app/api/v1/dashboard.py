from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.document import Document, DocumentStatus
from app.models.user import User


router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/stats")
def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> dict[str, int]:
    rows = (
        db.query(Document.status, func.count(Document.id))
        .filter(Document.owner_id == current_user.id)
        .group_by(Document.status)
        .all()
    )
    by_status = {status.value: count for status, count in rows}
    total = sum(by_status.values())
    return {
        "total_documents": total,
        "uploaded_documents": by_status.get(DocumentStatus.UPLOADED.value, 0),
        "processing_documents": by_status.get(DocumentStatus.PROCESSING.value, 0),
        "processed_documents": by_status.get(DocumentStatus.PROCESSED.value, 0),
        "failed_documents": by_status.get(DocumentStatus.FAILED.value, 0),
    }
