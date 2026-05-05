import csv
from pathlib import Path


def extract_text_from_file(storage_path: str, content_type: str) -> str:
    path = Path(storage_path)
    suffix = path.suffix.lower()

    if suffix == ".txt":
        return path.read_text(encoding="utf-8", errors="ignore")

    if suffix == ".csv":
        return _extract_csv(path)

    if suffix == ".pdf":
        return _extract_pdf(path)

    if suffix == ".docx":
        return _extract_docx(path)

    return ""


def _extract_csv(path: Path) -> str:
    rows: list[str] = []
    with path.open(newline="", encoding="utf-8", errors="ignore") as handle:
        reader = csv.reader(handle)
        for index, row in enumerate(reader, start=1):
            rows.append(f"Row {index}: " + " | ".join(cell.strip() for cell in row))
    return "\n".join(rows)


def _extract_pdf(path: Path) -> str:
    try:
        from pypdf import PdfReader
    except ImportError as exc:
        raise RuntimeError("PDF extraction requires pypdf. Install backend requirements.") from exc

    reader = PdfReader(str(path))
    pages: list[str] = []
    for page_number, page in enumerate(reader.pages, start=1):
        text = page.extract_text() or ""
        if text.strip():
            pages.append(f"Page {page_number}:\n{text.strip()}")
    return "\n\n".join(pages)


def _extract_docx(path: Path) -> str:
    try:
        from docx import Document
    except ImportError as exc:
        raise RuntimeError("DOCX extraction requires python-docx. Install backend requirements.") from exc

    document = Document(str(path))
    paragraphs = [paragraph.text.strip() for paragraph in document.paragraphs if paragraph.text.strip()]
    return "\n".join(paragraphs)
