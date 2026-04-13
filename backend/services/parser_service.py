import tempfile
import os
from pathlib import Path

DOCLING_FORMATS = {".pdf", ".docx", ".html", ".htm", ".md", ".markdown"}
TEXT_FORMATS = {".txt", ".text", ".csv"}


def parse_document(content: bytes, filename: str) -> str:
    ext = Path(filename).suffix.lower()

    if ext in TEXT_FORMATS:
        return content.decode("utf-8", errors="replace")

    if ext in DOCLING_FORMATS:
        return _parse_with_docling(content, filename)

    # Fallback: try UTF-8 decode
    return content.decode("utf-8", errors="replace")


def _parse_with_docling(content: bytes, filename: str) -> str:
    from docling.document_converter import DocumentConverter

    with tempfile.NamedTemporaryFile(suffix=Path(filename).suffix, delete=False) as tmp:
        tmp.write(content)
        tmp_path = tmp.name

    try:
        converter = DocumentConverter()
        result = converter.convert(tmp_path)
        return result.document.export_to_markdown()
    finally:
        os.unlink(tmp_path)
