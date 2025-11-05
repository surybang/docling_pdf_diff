"""
App Streamlit pour comparer 2 PDF (Docling → Markdown → Diff).
"""

import os
import re
import difflib
import tempfile
from typing import Tuple

import streamlit as st
from docling.document_converter import DocumentConverter


# =====================
# Helpers
# =====================
def _normalize_text(
    s: str,
    squeeze_spaces: bool = True,
    fix_hyphens: bool = True,
    strip_headers: bool = False,
) -> str:
    """Normalisations simples pour améliorer la qualité du diff."""
    if not s:
        return ""
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    if squeeze_spaces:
        s = re.sub(r"[ \t\u00A0\u2009\u2002\u2003]+", " ", s)
        s = re.sub(r"[ \t]+\n", "\n", s)
    if fix_hyphens:
        s = re.sub(r"(\w)-\n(\w)", lambda m: m.group(1) + m.group(2), s)
    if strip_headers:
        lines = s.splitlines()
        counts = {}
        for line in lines:
            key = line.strip()
            if key:
                counts[key] = counts.get(key, 0) + 1
        repeated = {k for k, v in counts.items() if v > 3 and len(k) < 60}
        lines = [ln for ln in lines if ln.strip() not in repeated]
        s = "\n".join(lines)
    return s


def extract_text_docling_from_bytes(pdf_bytes: bytes) -> str:
    """
    Écrit le PDF dans un fichier temporaire puis appelle Docling avec le PATH.
    """
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
        tmp.write(pdf_bytes)
        tmp_path = tmp.name
    try:
        converter = DocumentConverter()
        result = converter.convert(tmp_path)
        doc = getattr(result, "document", None)
        if doc is None:
            return str(result)

        if hasattr(doc, "export_to_markdown"):
            return doc.export_to_markdown()
        # Compat éventuelle
        for attr in ("to_markdown", "export_markdown", "export_text", "to_text"):
            if hasattr(doc, attr):
                return getattr(doc, attr)()
        return str(result)
    finally:
        try:
            os.remove(tmp_path)
        except Exception:
            pass


ESS = """
<style>
/**** Affinage du tableau de diff ****/
.diff { font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace; }
</style>
"""


def make_html_diff(a: str, b: str, fromdesc: str = "Version A", todesc: str = "Version B") -> str:
    a_lines = a.splitlines()
    b_lines = b.splitlines()
    diff = difflib.HtmlDiff(wrapcolumn=120)
    html = diff.make_file(a_lines, b_lines, fromdesc, todesc)
    return ESS + html


def summarize_diff(a: str, b: str) -> Tuple[int, int, int]:
    diff = list(difflib.ndiff(a.splitlines(), b.splitlines()))
    insertions = sum(1 for d in diff if d.startswith("+ "))
    deletions = sum(1 for d in diff if d.startswith("- "))
    changes = insertions + deletions
    return changes, insertions, deletions


# =====================
# UI Streamlit
# =====================
st.set_page_config(page_title="Comparateur PDF (Docling → Diff)", layout="wide")
st.title("🔍 Comparateur de PDF – Docling")
st.caption("Extraction Docling → normalisation → diff")

with st.sidebar:
    st.header("Normalisation")
    opt_spaces = st.checkbox("Compacter les espaces", value=True)
    opt_hyphens = st.checkbox("Recoller les mots coupés", value=True)
    opt_headers = st.checkbox("Retirer en-têtes/pieds récurrents (heuristique)", value=False)

col1, col2 = st.columns(2)
with col1:
    file_a = st.file_uploader("PDF #1 (Version A)", type=["pdf"], key="pdf_a")
with col2:
    file_b = st.file_uploader("PDF #2 (Version B)", type=["pdf"], key="pdf_b")

if file_a and file_b:
    pdf_a_bytes = file_a.read()
    pdf_b_bytes = file_b.read()

    # Extraction Docling
    text_a = extract_text_docling_from_bytes(pdf_a_bytes)
    text_b = extract_text_docling_from_bytes(pdf_b_bytes)

    # Normalisation
    text_a = _normalize_text(
        text_a, squeeze_spaces=opt_spaces, fix_hyphens=opt_hyphens, strip_headers=opt_headers
    )
    text_b = _normalize_text(
        text_b, squeeze_spaces=opt_spaces, fix_hyphens=opt_hyphens, strip_headers=opt_headers
    )

    # Aperçu (30 premières lignes)
    with st.expander("Aperçu texte (premières lignes)"):
        prev_cols = st.columns(2)
        with prev_cols[0]:
            st.subheader("Version A – extrait")
            st.text("\n".join(text_a.splitlines()[:30]))
        with prev_cols[1]:
            st.subheader("Version B – extrait")
            st.text("\n".join(text_b.splitlines()[:30]))

    # Métriques
    changes, ins, dels = summarize_diff(text_a, text_b)
    m1, m2, m3 = st.columns(3)
    m1.metric("Lignes modifiées", changes)
    m2.metric("Insertions (+)", ins)
    m3.metric("Suppressions (-)", dels)

    # Diff HTML
    html = make_html_diff(text_a, text_b, fromdesc=file_a.name, todesc=file_b.name)

    # Export / Affichage
    st.download_button(
        label="💾 Télécharger le diff HTML",
        data=html.encode("utf-8"),
        file_name=f"diff_{os.path.splitext(file_a.name)[0]}_vs_{os.path.splitext(file_b.name)[0]}.html",
        mime="text/html",
        use_container_width=True,
    )

    st.divider()
    st.subheader("Diff côte à côte")
    st.caption("Astuce : ouvrez en pleine largeur (clic sur ↗️) si nécessaire.")
    st.components.v1.html(html, height=600, scrolling=True)

else:
    st.info("Chargez deux fichiers PDF pour commencer.")
