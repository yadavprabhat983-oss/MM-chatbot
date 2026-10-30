from typing import List, Dict, Any

def chunk_text(
    text: str,
    chunk_size: int = 500,
    chunk_overlap: int = 100
) -> List[Dict[str, Any]]:
    """
    Splits text into overlapping chunks respecting line/sentence boundaries when possible.
    Returns list of dicts with chunk_index, text, and character length.
    """
    if not text or not text.strip():
        return []

    if chunk_size <= 0:
        chunk_size = 500
    if chunk_overlap >= chunk_size:
        chunk_overlap = max(0, chunk_size // 4)

    # Split roughly by paragraphs or sentences
    paragraphs = text.split("\n\n")
    chunks: List[str] = []
    current_chunk = ""

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # If adding this paragraph exceeds chunk_size
        if len(current_chunk) + len(para) + 2 > chunk_size:
            if current_chunk:
                chunks.append(current_chunk.strip())
                # Start new chunk with overlap from the end of current_chunk
                overlap_text = current_chunk[-chunk_overlap:].strip() if chunk_overlap > 0 else ""
                current_chunk = overlap_text + ("\n\n" if overlap_text else "") + para
            else:
                # The paragraph itself is larger than chunk_size, split by sentences or hard length
                start = 0
                while start < len(para):
                    end = start + chunk_size
                    part = para[start:end]
                    chunks.append(part.strip())
                    start += (chunk_size - chunk_overlap)
                current_chunk = ""
        else:
            if current_chunk:
                current_chunk += "\n\n" + para
            else:
                current_chunk = para

    if current_chunk.strip():
        chunks.append(current_chunk.strip())

    # Format result list
    result = []
    for idx, c_text in enumerate(chunks):
        if c_text:
            result.append({
                "chunk_index": idx,
                "text": c_text,
                "char_length": len(c_text)
            })

    return result
