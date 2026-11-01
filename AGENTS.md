# AGENTS.md — FORMINDEX

Guidance for agents working in this repository.

## What this repository is

An analysis platform for the FORMIS myrmecological bibliography (~80,000 ant
literature records). It reads FORMIS exports, builds publication-trend and
co-authorship views, and generates targeted bibliographies plus LLM-assisted
summaries, translations, and audio.

Published archive: doi:10.5281/zenodo.13927024.

It is a **script collection, not a package**. There is no `pyproject.toml` or
`setup.py`, no importable distribution, no CI, and no build step. Do not add
packaging metadata to "modernise" it; the value is in the analyses and the
committed outputs.

## Layout

| Path | Role |
|---|---|
| `Initial_Files/` | Raw FORMIS exports (BibTeX, Excel, EndNote, and a 316-record sample). Inputs, not generated |
| `Scripts/` | `Read_in_FORMIS.py`, `Keyword_Analysis.py`, `Location_Analysis.py`, `Generate_Target_Bibliographies.py` |
| `Methods/` | `FORMINDEX_Methods.py` — shared analysis methods |
| `LLM_Methods/` | Numbered pipeline: `1_generate_pro-summaries.py`, `2_llm_write_summary.py`, `3_translate_summary.py`; `Inputs_and_Outputs/` |
| `Perplexity_Methods/` | `Perplexity.py`, `Simple_Perplexity.py`, `System_Prompts.json`, `Markdown_Output/` |
| `Prompts/` | Prompt text used by the LLM steps |
| `Visualizations/` | Per-topic literature output folders |
| `Targeted_Bibliographies/` | Generated topic bibliographies (e.g. Ant-plant symbioses, Bioenergetics) |
| `Reports/` | Dated PDF reports |
| `docs/` | Documentation hub |

The numbered prefixes in `LLM_Methods/` are execution order. Keep them ordered;
do not renumber.

## Running

Scripts are run directly with `python3` from the repository root. Dependencies
come from whatever is already installed — there is no lockfile. Confirm the
imports a script needs before running it, and prefer adding a requirements file
over silently widening the environment.

## API keys

`LLM_Methods/` and `Perplexity_Methods/` call external model APIs. Supply
credentials through the environment or a local file that is not committed.
Nothing tracked in this repository may contain a key. If you find a committed
key file, remove it from the index and rotate the key.

## Conventions

- `Initial_Files/` is the immutable input set. Never overwrite an export in
  place; add a dated file instead.
- Generated bibliographies, summaries, and reports are committed on purpose so
  readers can inspect results without re-running paid API calls. Regenerating
  them is fine; hand-editing them is not.
- Citations must carry a DOI where one exists. Do not assert a bibliometric
  total that the scripts did not compute.
- The FORMIS database is third-party material. Respect its fair-use terms; do
  not redistribute bulk records beyond what the export already permits.

## Verification

There is no automated gate and one test file (`test_env.py`). Verify a change by
running the affected script against a small slice of `Initial_Files/` and
reporting the command and the output you inspected.
