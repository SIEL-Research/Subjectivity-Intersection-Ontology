#!/usr/bin/env python3
"""Generate the categorical N1–N6 comparison matrix as SVG and PDF."""

from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.colors import BoundaryNorm, ListedColormap


ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = ROOT / "data" / "comparative-assessments.csv"
OUTPUT_DIR = ROOT / "output"

STATUS_ORDER = [
    "Non-satisfaction",
    "Partial",
    "Clear satisfaction",
    "Insufficient evidence",
]
STATUS_VALUE = {status: index for index, status in enumerate(STATUS_ORDER)}
STATUS_CODE = {
    "Non-satisfaction": "N",
    "Partial": "P",
    "Clear satisfaction": "C",
    "Insufficient evidence": "I",
}
STATUS_COLOR = {
    "Non-satisfaction": "#E6E9ED",
    "Partial": "#D9A441",
    "Clear satisfaction": "#2D7A69",
    "Insufficient evidence": "#9C8AC7",
}


def read_assessments() -> tuple[list[str], list[str], list[list[str]]]:
    with DATA_PATH.open(encoding="utf-8", newline="") as handle:
        rows = list(csv.DictReader(handle))
    criteria = [f"N{i}" for i in range(1, 7)]
    cases = [row["Comparison Case"] for row in rows]
    statuses = [[row[criterion] for criterion in criteria] for row in rows]
    unknown = sorted({value for row in statuses for value in row} - set(STATUS_ORDER))
    if unknown:
        raise ValueError(f"Unrecognized assessment categories: {unknown}")
    return cases, criteria, statuses


def main() -> None:
    cases, criteria, statuses = read_assessments()
    values = [[STATUS_VALUE[value] for value in row] for row in statuses]

    colors = [STATUS_COLOR[status] for status in STATUS_ORDER]
    cmap = ListedColormap(colors)
    norm = BoundaryNorm([-0.5, 0.5, 1.5, 2.5, 3.5], cmap.N)

    fig, ax = plt.subplots(figsize=(10.8, 9.4), constrained_layout=True)
    ax.imshow(values, cmap=cmap, norm=norm, aspect="auto", interpolation="nearest")

    ax.set_xticks(range(len(criteria)), labels=criteria, fontsize=11, fontweight="bold")
    ax.xaxis.tick_top()
    ax.set_yticks(range(len(cases)), labels=cases, fontsize=9.4)
    ax.tick_params(axis="both", length=0, pad=8)

    for row_index, row in enumerate(statuses):
        for column_index, status in enumerate(row):
            text_color = "white" if status == "Clear satisfaction" else "#18212B"
            ax.text(
                column_index,
                row_index,
                STATUS_CODE[status],
                ha="center",
                va="center",
                color=text_color,
                fontsize=10.5,
                fontweight="bold",
            )

    ax.set_xticks([index - 0.5 for index in range(1, len(criteria))], minor=True)
    ax.set_yticks([index - 0.5 for index in range(1, len(cases))], minor=True)
    ax.grid(which="minor", color="white", linewidth=1.4)
    ax.tick_params(which="minor", bottom=False, left=False)
    ax.axvline(4.5, color="#263746", linewidth=2.6)

    for spine in ax.spines.values():
        spine.set_visible(False)

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    metadata = {"Title": "Distribution of criterion-level assessments across the comparison set"}
    svg_path = OUTPUT_DIR / "figure-4-comparative-matrix.svg"
    fig.savefig(svg_path, bbox_inches="tight", metadata=metadata)
    fig.savefig(OUTPUT_DIR / "figure-4-comparative-matrix.pdf", bbox_inches="tight", metadata=metadata)
    plt.close(fig)

    # Matplotlib emits trailing spaces in multiline SVG path data. Normalize
    # the generated text so repository whitespace checks remain clean.
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
