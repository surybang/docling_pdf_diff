"""Streamlit app for comparing two PDFs using Docling and difflib."""

import os

import streamlit as st

from docling_pdf_diff.core import (
    extract_text_docling_from_bytes,
    make_html_diff,
    normalize_text,
    summarize_diff,
)


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

    try:
        text_a = extract_text_docling_from_bytes(pdf_a_bytes)
        text_b = extract_text_docling_from_bytes(pdf_b_bytes)
    except RuntimeError as exc:
        st.error(str(exc))
        st.stop()

    text_a = normalize_text(
        text_a,
        squeeze_spaces=opt_spaces,
        fix_hyphens=opt_hyphens,
        strip_headers=opt_headers,
    )
    text_b = normalize_text(
        text_b,
        squeeze_spaces=opt_spaces,
        fix_hyphens=opt_hyphens,
        strip_headers=opt_headers,
    )

    with st.expander("Aperçu texte (premières lignes)"):
        preview_left, preview_right = st.columns(2)
        with preview_left:
            st.subheader("Version A – extrait")
            st.text("\n".join(text_a.splitlines()[:30]))
        with preview_right:
            st.subheader("Version B – extrait")
            st.text("\n".join(text_b.splitlines()[:30]))

    changes, insertions, deletions = summarize_diff(text_a, text_b)
    metric_columns = st.columns(3)
    metric_columns[0].metric("Lignes modifiées", changes)
    metric_columns[1].metric("Insertions (+)", insertions)
    metric_columns[2].metric("Suppressions (-)", deletions)

    html = make_html_diff(text_a, text_b, fromdesc=file_a.name, todesc=file_b.name)

    output_name = (
        f"diff_{os.path.splitext(file_a.name)[0]}"
        f"_vs_{os.path.splitext(file_b.name)[0]}.html"
    )

    st.download_button(
        label="💾 Télécharger le diff HTML",
        data=html.encode("utf-8"),
        file_name=output_name,
        mime="text/html",
        use_container_width=True,
    )

    st.divider()
    st.subheader("Diff côte à côte")
    st.caption("Astuce : ouvrez en pleine largeur (clic sur ↗️) si nécessaire.")
    st.components.v1.html(html, height=600, scrolling=True)
else:
    st.info("Chargez deux fichiers PDF pour commencer.")
