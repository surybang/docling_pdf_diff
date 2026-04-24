"""Package entrypoint for docling_pdf_diff utilities."""

from .core import extract_text_docling_from_bytes, make_html_diff, normalize_text, summarize_diff

__all__ = [
    "extract_text_docling_from_bytes",
    "make_html_diff",
    "normalize_text",
    "summarize_diff",
]
