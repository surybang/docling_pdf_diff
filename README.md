# Docling pdf diff

Outil minimaliste pour **comparer deux fichiers PDF**, en s'appuyant sur [Docling](https://github.com/DS4SD/docling) pour l'extraction du texte et `difflib` pour la génération du diff.

L'interface Streamlit permet d'uploader deux PDFs, de visualiser les différences ligne par ligne, et d'exporter le résultat en HTML.

---

## Installation

Le projet utilise [uv](https://github.com/astral-sh/uv) comme gestionnaire de paquets (Python ≥ 3.11 requis).

```bash
# Cloner le repo
git clone https://github.com/surybang/docling_pdf_diff.git
cd docling_pdf_diff

# Installer les dépendances
uv sync
```

> Sur Linux, Docling dépend d'une bibliothèque native pour OpenCV.
> Si vous obtenez `libGL.so.1: cannot open shared object file`, installez les paquets suivants :
>
> ```bash
> sudo apt-get install libgl1 libgl1-mesa-dri libgl1-amber-dri
> ```
>
> Selon votre distribution, certains paquets peuvent déjà être satisfaits ou non disponibles.
> Si une installation échoue, utilisez `apt-cache search '^libgl1'` pour trouver le package adapté.
>
> ```bash
> apt-cache search '^libgl1'
> ```

> **Note :** Docling est une librairie lourde (~plusieurs Go avec ses modèles).

---

## Utilisation

```bash
uv run streamlit run streamlit.py
```

L'application s'ouvre sur `http://localhost:8501`.

1. Uploader **PDF #1 (Version A)** et **PDF #2 (Version B)**
2. Ajuster les options de normalisation dans la sidebar si nécessaire
3. Consulter les métriques et le diff côte à côte
4. Télécharger le diff HTML via le bouton dédié

---

## Structure

```
docling_pdf_diff/
├── docling_pdf_diff/   # Package utilitaire pour l'extraction et le diff
│   ├── __init__.py
│   └── core.py
├── streamlit.py        # Interface Streamlit
├── pyproject.toml      # Dépendances (uv)
└── uv.lock             # Lockfile uv
```

---

## Dépendances principales

| Package | Rôle |
|---|---|
| `docling >= 2.60.1` | Extraction PDF → Markdown |
| `streamlit >= 1.51.0` | Interface web |
| `difflib` | Génération du diff |

---

## Options de normalisation

| Option | Description |
|---|---|
| Compacter les espaces | Réduit les espaces multiples et tabulations |
| Recoller les mots coupés | Supprime les coupures de mots en fin de ligne (`-\n`) |
| Retirer les en-têtes récurrents | Supprime les lignes répétées plus de 3 fois (heuristique) |

---
