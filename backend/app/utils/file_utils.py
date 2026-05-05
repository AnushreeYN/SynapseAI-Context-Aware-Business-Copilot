from pathlib import Path


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".csv", ".txt"}
ALLOWED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "text/csv",
    "text/plain",
    "application/csv",
}


def is_allowed_file(filename: str, content_type: str | None) -> bool:
    suffix = Path(filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        return False
    return content_type in ALLOWED_CONTENT_TYPES if content_type else True


def safe_extension(filename: str) -> str:
    return Path(filename).suffix.lower()
