"""
File upload and text extraction utilities.
Supports: .txt, .md, .pdf, .docx
"""
import os
import re
from pathlib import Path
from typing import Optional


def extract_text_from_file(file_path: str) -> Optional[str]:
    """
    Extract text content from uploaded file.
    Supports: .txt, .md, .pdf, .docx
    """
    path = Path(file_path)
    suffix = path.suffix.lower()

    if suffix in ('.txt', '.md'):
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            return f.read()

    elif suffix == '.pdf':
        try:
            import PyPDF2
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text_parts = []
                for page in reader.pages:
                    text_parts.append(page.extract_text() or '')
                return '\n\n'.join(text_parts)
        except ImportError:
            raise ImportError("PyPDF2 is required for PDF support. Install with: pip install PyPDF2")

    elif suffix == '.docx':
        try:
            import docx
            doc = docx.Document(file_path)
            return '\n\n'.join([para.text for para in doc.paragraphs if para.text.strip()])
        except ImportError:
            raise ImportError("python-docx is required for DOCX support. Install with: pip install python-docx")

    else:
        raise ValueError(f"Unsupported file type: {suffix}. Supported: .txt, .md, .pdf, .docx")


def chunk_text(text: str, chunk_size: int = 1500, overlap: int = 200) -> list[str]:
    """
    Split text into overlapping chunks for embedding.
    """
    if not text or not text.strip():
        return []

    # Clean text
    text = re.sub(r'\n{3,}', '\n\n', text.strip())

    if len(text) <= chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size

        # Try to break at a paragraph or sentence boundary
        if end < len(text):
            # Look for paragraph break
            para_break = text.rfind('\n\n', start + chunk_size // 2, end + 200)
            if para_break > start:
                end = para_break
            else:
                # Look for sentence boundary
                sent_break = max(
                    text.rfind('. ', start + chunk_size // 2, end),
                    text.rfind('! ', start + chunk_size // 2, end),
                    text.rfind('? ', start + chunk_size // 2, end)
                )
                if sent_break > start:
                    end = sent_break + 1

        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)

        start = end - overlap

    return chunks
