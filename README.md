# MangaFlow 📖

AI-powered manga translation and colorization agent built for the **Google Cloud Rapid Agent Hackathon 2026**.

## Stack
- **Google ADK** — multi-agent orchestration (SequentialAgent)
- **Gemini** — vision detection, translation, image editing & colorization
- **Elastic** — Translation Memory, Glossary, Quality Scores (via MCP)

## Setup

```bash
# 1. Clone & install
cd mangaflow
python -m venv venv && venv\Scripts\activate
pip install -r requirements.txt

# 2. Configure
cp .env.example .env   # fill in GOOGLE_API_KEY, ES_URL, ES_API_KEY

# 3. Set up Elasticsearch
python elastic_setup/create_indices.py
python scripts/seed_demo_data.py
```

## Running a Translation

Point the script at any folder of existing raw manga images (JPG / PNG / WEBP):

```bash
# Translate chapter 1, with colorization
python scripts/run_translation.py --folder "C:/my-manga/chapter-01" --title "Dragon Spirit" --chapter 1

# Skip colorization
python scripts/run_translation.py --folder "C:/my-manga/chapter-01" --title "Dragon Spirit" --no-colorize

# Or run interactively via the ADK Web UI
adk web agents/
```

### CLI Options

| Flag | Default | Description |
|------|---------|-------------|
| `--folder` | *(required)* | Path to folder of raw manga page images |
| `--title` | `Unknown Manga` | Series title (used for Elastic indexing) |
| `--chapter` | `1` | Chapter number |
| `--no-colorize` | — | Skip the colorization step |

Translated pages are saved to `output/<title>/chapter_<N>/`.

## Agent Pipeline

```
User prompt
  └─ MangaFlow Orchestrator (root_agent)
       └─ page_translation_pipeline (SequentialAgent)
            ├─ detector_agent      → finds all text regions (Gemini vision)
            ├─ translator_agent    → JP→EN with Elastic glossary + memory
            ├─ cleaner_agent       → removes JP text, typesets EN (Gemini img edit)
            ├─ colorizer_agent     → colorizes B&W page (Gemini img gen)
            └─ quality_agent       → scores output, flags issues
```

## Elasticsearch Indices

| Index | Purpose |
|-------|---------|
| `translation-memory` | Stores all JP→EN translations for reuse |
| `manga-glossary` | Character/place/attack canonical names |
| `manga-pages` | Page processing progress |
| `quality-scores` | Per-page quality metrics |
| `color-references` | Character color palettes for colorization |
