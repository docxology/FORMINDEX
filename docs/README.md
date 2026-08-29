# FORMINDEX — Documentation

**FORMINDEX** (FORMIS INtegrated Database EXploration; DOI
10.5281/zenodo.13927024) analyzes and visualizes the FORMIS myrmecological
database (~80,000 records, July 2024 export), combining bibliometrics, LLM
integration, and interactive visualizations.

## Layout

- `Methods/FORMINDEX_Methods.py` — core method implementation
- `Scripts/` — `Read_in_FORMIS.py`, `Keyword_Analysis.py`, `Location_Analysis.py`,
  `Visualize_FORMIS.py`, `Generate_Target_Bibliographies.py`
- `LLM_Methods/`, `Prompts/` — LLM-driven analysis and prompt assets
- `Perplexity_Methods/` — Perplexity-based retrieval methods
- `Targeted_Bibliographies/`, `Visualizations/`, `Reports/` — generated outputs
- `Initial_Files/` — input data
- `ToDo.md` — community task list for maintaining FORMIS

## Run / test

Not documented in repo — needs owner input (no pyproject.toml, package.json, or
Makefile is present; run commands are not stated in README.md).

## Status

Docs hub created by the docs-audit pass (2026-08-29).
