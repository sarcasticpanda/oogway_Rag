from typing import List, Dict, Any

def chunk_transcript(
    text: str,
    chunk_size: int = 1800,
    chunk_overlap: int = 250
) -> List[Dict[str, Any]]:
    """
    Split podcast transcript text into overlapping chunks.
    Preserves line breaks and speaker turns where possible.
    """
    if not text:
        return []

    lines = text.split("\n")
    chunks = []
    current_chunk = []
    current_length = 0

    for line in lines:
        line_len = len(line) + 1
        if current_length + line_len > chunk_size and current_chunk:
            chunk_str = "\n".join(current_chunk).strip()
            if chunk_str:
                chunks.append(chunk_str)

            # Keep the last few lines for overlap
            overlap_chunk = []
            overlap_len = 0
            for prev_line in reversed(current_chunk):
                if overlap_len + len(prev_line) + 1 <= chunk_overlap:
                    overlap_chunk.insert(0, prev_line)
                    overlap_len += len(prev_line) + 1
                else:
                    break

            current_chunk = overlap_chunk
            current_length = overlap_len

        current_chunk.append(line)
        current_length += line_len

    if current_chunk:
        chunk_str = "\n".join(current_chunk).strip()
        if chunk_str:
            chunks.append(chunk_str)

    return [{"index": i, "text": c} for i, c in enumerate(chunks)]
