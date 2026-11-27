"""Check the retained FORMIS sample and optionally plot aggregate record types."""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path
from tempfile import TemporaryDirectory

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from Methods.FORMINDEX_Methods import export_to_json, load_bibtex
from Scripts.Generate_Target_Bibliographies import (
    TARGET_BIBLIOGRAPHIES,
    generate_targeted_bibliographies,
    load_formis_data,
    save_targeted_bibliographies,
)

SAMPLE = "FORMIS 2024(July)-Bibtext_316_sample.txt"
EXPECTED_TYPES = {
    "article": 198,
    "techreport": 85,
    "incollection": 28,
    "phdthesis": 4,
    "book": 2,
}


def verify(sample):
    records = load_bibtex(sample)
    types = Counter(record["ref_type"] for record in records)
    headers = sum(
        line.strip().startswith("@")
        for line in sample.read_text(encoding="utf-8-sig").splitlines()
    )
    targets = generate_targeted_bibliographies(records)
    assert len(records) == headers == 317
    assert types == EXPECTED_TYPES
    assert len(TARGET_BIBLIOGRAPHIES) == 23
    assert len(targets) == 15
    memberships = sum(map(len, targets.values()))
    assert memberships == 580
    assert len(targets["Foraging"]) == 47
    notes_with_boilerplate = sum(
        "part of formis" in record.get("note", "").lower() for record in records
    )
    assert notes_with_boilerplate == len(targets["Art"]) == len(records)

    with TemporaryDirectory() as temp:
        path = Path(temp)
        export_to_json(records, path / "sample.json")
        assert load_formis_data(path / "sample.json") == records
        save_targeted_bibliographies(targets, path / "targets")
        files = sorted((path / "targets").glob("*/*_bibliography.json"))
        assert len(files) == len(targets)
        for file in files:
            assert load_formis_data(file) == targets[file.parent.name]

    return {
        "sample_headers": headers,
        "record_types": dict(types.most_common()),
        "configured_targets": len(TARGET_BIBLIOGRAPHIES),
        "nonempty_targets": len(targets),
        "target_memberships": memberships,
        "art_matches": len(targets["Art"]),
        "foraging_matches": len(targets["Foraging"]),
        "notes_with_part_of_formis": notes_with_boilerplate,
    }


def plot_types(types, destination):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    labels = ["Article", "Technical report", "Collection chapter", "PhD thesis", "Book"]
    figure, axis = plt.subplots(figsize=(7, 3.2), layout="constrained")
    bars = axis.barh(labels, list(types.values()), color="#24666e")
    axis.invert_yaxis()
    axis.bar_label(bars, padding=4)
    axis.set_xlim(0, max(types.values()) * 1.16)
    axis.set_xlabel("Parsed records")
    axis.spines[["top", "right"]].set_visible(False)
    destination.parent.mkdir(parents=True, exist_ok=True)
    figure.savefig(destination, dpi=180)
    plt.close(figure)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--sample",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "Initial_Files" / SAMPLE,
    )
    parser.add_argument("--figure", type=Path)
    args = parser.parse_args()
    summary = verify(args.sample)
    if args.figure:
        plot_types(summary["record_types"], args.figure)
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
