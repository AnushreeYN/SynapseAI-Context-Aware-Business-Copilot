from pathlib import Path
from uuid import uuid4

from fastapi import UploadFile

from app.core.config import settings
from app.utils.file_utils import safe_extension


class LocalStorageService:
    def __init__(self, upload_dir: Path | None = None) -> None:
        self.upload_dir = upload_dir or settings.UPLOAD_DIR
        self.upload_dir.mkdir(parents=True, exist_ok=True)

    async def save_upload(self, file: UploadFile, owner_id: int) -> tuple[str, str, int]:
        extension = safe_extension(file.filename or "")
        stored_filename = f"user-{owner_id}-{uuid4().hex}{extension}"
        storage_path = self.upload_dir / stored_filename

        size = 0
        with storage_path.open("wb") as destination:
            while chunk := await file.read(1024 * 1024):
                size += len(chunk)
                destination.write(chunk)

        await file.seek(0)
        return stored_filename, str(storage_path), size

    def delete(self, storage_path: str) -> None:
        path = Path(storage_path)
        if path.exists() and path.is_file():
            path.unlink()


storage_service = LocalStorageService()
