# Docling pdf diff

Outil minimaliste pour **comparer deux fichiers PDF côte à côte**, en s'appuyant sur [Docling](https://github.com/DS4SD/docling) pour l'extraction du texte et `difflib` pour la génération du diff.

L'interface Streamlit permet d'uploader deux PDFs, de visualiser les différences ligne par ligne, et d'exporter le résultat en HTML.

---

## Fonctionnalités

- **Extraction intelligente** : Docling convertit les PDFs en Markdown structuré (gère les PDFs natifs et scannés)
- **Normalisation configurable** : compactage des espaces, recollage des mots coupés en fin de ligne, suppression heuristique des en-têtes/pieds de page récurrents
- **Diff côte à côte** : vue HTML colorée (insertions en vert, suppressions en rouge)
- **Métriques synthétiques** : nombre de lignes modifiées, insertions, suppressions
- **Export HTML** : téléchargement du diff complet pour archivage ou partage
- **UI Streamlit** : interface web légère, sans configuration

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
├── streamlit.py       # Interface Streamlit + logique de diff
├── pyproject.toml     # Dépendances (uv)
└── uv.lock            # Lockfile uv
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
