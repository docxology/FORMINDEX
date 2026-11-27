# Local bibliographic workflow

## Verify the retained sample

Use Python 3.11 or newer in an isolated environment. The shared methods
import the plotting and text-analysis libraries even for parsing. Install
these before running the offline check.

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install chardet==5.2.0 matplotlib seaborn wordcloud scikit-learn numpy scipy
python Scripts/Verify_FORMIS_Sample.py
```

The verifier uses the tracked sample in `Initial_Files/`, checks record
types, topic memberships and the `Art` substring artifact, and checks
exact JSON round trips with the existing exporters in a temporary directory.
The receipt contains aggregate counts. Use `--sample PATH` for another
copy of the same fixture, and `--figure PATH` to write the manuscript chart.

## Work with the full export

Use a disposable copy when regenerating the retained artifacts. The
following scripts have fixed paths rather than flags.

| Script | Input and behavior |
| --- | --- |
| [Read_in_FORMIS.py](../Scripts/Read_in_FORMIS.py) | Calls pip in a script-local virtual environment on direct invocation, then reads the full BibTeX input and writes the sibling `FORMIS_2024_July_Bibtex.json`. Install the shared imports in the invoking interpreter too. |
| [Generate_Target_Bibliographies.py](../Scripts/Generate_Target_Bibliographies.py) | Reads the converted JSON and writes `Targeted_Bibliographies/<term>/<term>_bibliography.json` for each matched term. Edit `TARGET_BIBLIOGRAPHIES` to change the list. Multiple membership and substring collisions are possible. |
| [Visualize_FORMIS.py](../Scripts/Visualize_FORMIS.py) | Reads the full and targeted JSONs and writes per-topic outputs under `Visualizations/`. Set `MPLBACKEND=Agg` in a headless session. |
| [Keyword_Analysis.py](../Scripts/Keyword_Analysis.py) | Reads the same full and targeted JSONs and writes keyword and location charts under `Visualizations/`. |
| [Location_Analysis.py](../Scripts/Location_Analysis.py) | Run from `Scripts/` so its relative paths resolve. Imports additional `geopandas` and `fuzzywuzzy` dependencies. Its publication map downloads Natural Earth country polygons. Keep this step separate from offline verification. |

Historical model scripts and their committed outputs remain under
`LLM_Methods/` and `Perplexity_Methods/`. The filename
`Perplexity_Methods/test_perplexity_api.py` denotes a manual live provider
request. The local sample check requires neither provider dependencies nor a
credential. The 2024 report also documents the use of NotebookLM to create
audio from selected bibliographies.

## Attribution and reuse

The July 2024 FORMIS records are third-party bibliographic material. The
FORMINDEX code license does not grant rights to underlying article text,
abstracts or other exported material. Keep raw exports as received, credit
FORMIS and the relevant publications, and check source reuse terms before
redistributing records. Retain the [dated reports](../Reports/) and their
[Zenodo archive](https://doi.org/10.5281/zenodo.13927024) as provenance.
