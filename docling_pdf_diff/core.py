"""Core utilities for PDF extraction, normalization and diff generation."""

import os
import re
import difflib
import tempfile
from typing import Tuple

from docling.document_converter import DocumentConverter

DEFAULT_DIFF_CSS = """
<style>
/**** Affinage du tableau de diff ****/
.diff { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas,
  "Liberation Mono", "Courier New", monospace; }
</style>
"""


def normalize_text(
    text: str,
    squeeze_spaces: bool = True,
    fix_hyphens: bool = True,
    strip_headers: bool = False,
) -> str:
    """Normalize extracted text before computing a diff."""
    if not text:
        return ""

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    if squeeze_spaces:
        text = re.sub(r"[ \t\u00A0\u2009\u2002\u2003]+", " ", text)
        text = re.sub(r"[ \t]+\n", "\n", text)

    if fix_hyphens:
        text = re.sub(r"(\w)-\n(\w)", lambda m: m.group(1) + m.group(2), text)

    if strip_headers:
        text = _remove_repeated_headers(text)

    return text


def _remove_repeated_headers(text: str) -> str:
    lines = text.splitlines()
    counts: dict[str, int] = {}
    for line in lines:
        key = line.strip()
        if key:
            counts[key] = counts.get(key, 0) + 1

    repeated = {key for key, value in counts.items() if value > 3 and len(key) < 60}
    filtered_lines = [line for line in lines if line.strip() not in repeated]
    return "\n".join(filtered_lines)


def extract_text_docling_from_bytes(pdf_bytes: bytes) -> str:
    """Extract text from a PDF byte stream using Docling."""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(pdf_bytes)
        tmp_path = tmp_file.name

    try:
        try:
            converter = DocumentConverter()
            result = converter.convert(tmp_path)
        except Exception as exc:
            if "libGL.so.1" in str(exc):
                raise RuntimeError(
                    "Docling requires the system library libGL.so.1. "
                    "On Debian/Ubuntu install libgl1 or libgl1-mesa-dri, "
                    "then relaunch the app."
                ) from exc
            raise RuntimeError(f"Docling extraction failed: {exc}") from exc

        document = getattr(result, "document", result)

        for export_method in (
            "export_to_markdown",
            "to_markdown",
            "export_markdown",
            "export_text",
            "to_text",
        ):
            if hasattr(document, export_method):
                return getattr(document, export_method)()

        return str(result)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


def make_html_diff(
    source_a: str,
    source_b: str,
    fromdesc: str = "Version A",
    todesc: str = "Version B",
) -> str:
    """Build an HTML diff view for two text versions."""
    diff = difflib.HtmlDiff(wrapcolumn=120)
    html = diff.make_file(source_a.splitlines(), source_b.splitlines(), fromdesc, todesc)
    return DEFAULT_DIFF_CSS + html


def summarize_diff(source_a: str, source_b: str) -> Tuple[int, int, int]:
    """Return total changes, insertions and deletions between two text versions."""
    diff_lines = difflib.ndiff(source_a.splitlines(), source_b.splitlines())
    insertions = sum(1 for line in diff_lines if line.startswith("+ "))
    deletions = sum(1 for line in diff_lines if line.startswith("- "))
    return insertions + deletions, insertions, deletions
