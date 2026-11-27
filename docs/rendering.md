# Build the manuscript

Use Git, uv, Python 3.14 or later for Template, Pandoc with a matching
pandoc-crossref, XeLaTeX, BibTeX and Poppler. From a committed FORMINDEX checkout, create an isolated project
under the pinned [Template renderer](https://github.com/docxology/template/tree/87704feae0a4490ef7dad9c931d268e8c30273c2).
A sparse checkout needs the canonical source, native scripts and the small
sample fixture. The renderer does not need the full export, archived model
outputs or any provider credentials.

```bash
set -e
source_checkout="$(pwd -P)"
source_commit="$(git rev-parse HEAD)"
scratch="$(mktemp -d)"
renderer="$scratch/template"
project="$renderer/projects/working/FORMINDEX"
sample='Initial_Files/FORMIS 2024(July)-Bibtext_316_sample.txt'

git clone https://github.com/docxology/template.git "$renderer"
git -C "$renderer" checkout --detach 87704feae0a4490ef7dad9c931d268e8c30273c2
mkdir -p "$renderer/projects/working"
git -C "$source_checkout" worktree add --no-checkout --detach "$project" "$source_commit"
printf '%s\n' '/*' '!/*/' '/docs/' '/Methods/' '/Scripts/' "/$sample" |
  git -C "$project" sparse-checkout set --no-cone --stdin
git -C "$project" read-tree -mu HEAD

cd "$renderer"
uv sync --locked
cd "$project"
"$source_checkout/.venv/bin/python" Scripts/Verify_FORMIS_Sample.py \
  --figure output/figures/formis-sample-types.png
cd "$renderer"
uv run --no-sync python scripts/pipeline/stage_03_render.py --project working/FORMINDEX
uv run --no-sync python scripts/pipeline/stage_04_validate.py --project working/FORMINDEX
printf '%s\n' "$project/output"
```

Prepare the source checkout's `.venv` as described in the
[local workflow](workflow.md) before running these commands. When finished,
remove the temporary worktree with `git worktree remove --force "$project"`
after copying any editions you want to keep.

The configured combined editions are under `output/pdf/` and
`output/web/index.html`. Check `output/reports/validation_report.json` and
`output/reports/rendered_provenance.json` for validation and the consumed
manuscript paths. The dated PDFs under [Reports](../Reports/) are retained
historical work.
