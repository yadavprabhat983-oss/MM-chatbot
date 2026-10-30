import io
from typing import Tuple
from app.core.errors import InvalidFileError
from app.core.logging import logger

SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf", ".docx"}

def extract_text_from_file(file_bytes: bytes, filename: str) -> Tuple[str, str]:
    """
    Extracts text from supported file formats.
    Returns (cleaned_text, detected_file_type).
    """
    filename_lower = filename.lower()
    ext = ""
    for candidate in SUPPORTED_EXTENSIONS:
        if filename_lower.endswith(candidate):
            ext = candidate
            break

    if not ext:
        raise InvalidFileError(
            f"Unsupported file format for '{filename}'. Supported extensions: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    clean_type = ext.lstrip(".")

    try:
        if ext in {".txt", ".md"}:
            try:
                text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                text = file_bytes.decode("latin-1", errors="replace")

        elif ext == ".pdf":
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            pages_text = []
            for i, page in enumerate(reader.pages):
                page_content = page.extract_text() or ""
                if page_content.strip():
                    pages_text.append(f"[Page {i+1}]\n{page_content}")
            text = "\n\n".join(pages_text)

        elif ext == ".docx":
            import docx
            doc = docx.Document(io.BytesIO(file_bytes))
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            text = "\n\n".join(paragraphs)

        else:
            raise InvalidFileError(f"Unsupported format: {ext}")

    except Exception as e:
        logger.error(f"Failed to extract text from {filename}: {e}")
        raise InvalidFileError(f"Could not parse document '{filename}': {str(e)}")

    cleaned = text.strip()
    if not cleaned:
        raise InvalidFileError(f"The document '{filename}' is empty or contains no extractable text.")

    return cleaned, clean_type
