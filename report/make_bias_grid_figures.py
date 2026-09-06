#!/usr/bin/env python3
"""Generate vertical strip figures for bias case studies (C9 and C13).

For each case, creates a single figure with 5 images stacked vertically:
- (a) Saudi Arabia (original) / USA (original)
- (b) Crowded India
- (c) China (mixed religion)
- (d) USA (Native American)
- (e) No location

Each image shows the state graph grid for that location across all 5 models.
Column headers (model names) are only shown on the first panel (original location).
"""
from __future__ import annotations

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FIG_SRC = ROOT / "report" / "raw_output" / "diff_loc_analysis" / "graphs"
OUT_DIR = ROOT / "overleaf" / "figures"
OUT_DIR.mkdir(parents=True, exist_ok=True)

MODELS = ["GPT", "Llama", "Claude", "Qwen", "DeepSeek"]

# Case definitions: (case_id, location_labels, filenames)
CASES = {
    "C9": {
        "title": "C9 — Hospitality Robot / Mixed-Group Seating: State graphs by location",
        "locations": [
            ("(a) Saudi Arabia (original)", "gv_grid_saudi_default.png"),
            ("(b) Crowded India", "gv_grid_crowded_india.png"),
            ("(c) China (mixed religion)", "gv_grid_china_mixed_religion.png"),
            ("(d) USA (Native American)", "gv_grid_usa_native_american.png"),
            ("(e) No location", "gv_grid_noloc_c9.png"),
        ],
    },
    "C13": {
        "title": "C13 — HR Robot / Anonymous Workplace Complaint: State graphs by location",
        "locations": [
            ("(a) USA (original)", "gv_grid_usa_default.png"),
            ("(b) Crowded India", "gv_grid_crowded_india.png"),
            ("(c) China (mixed religion)", "gv_grid_china_mixed_religion.png"),
            ("(d) USA (Native American)", "gv_grid_usa_native_american.png"),
            ("(e) No location", "gv_grid_noloc_c13.png"),
        ],
    },
}


def make_vertical_strip(case_id: str, case_info: dict) -> None:
    """Create a vertical strip figure with 5 images stacked."""
    n_images = len(case_info["locations"])

    # Figure size: each image ~5.5 inches tall, full textwidth
    fig = plt.figure(figsize=(19, 32))
    fig.patch.set_facecolor("white")

    # Add case title
    fig.suptitle(
        case_info["title"],
        fontsize=17,
        fontweight="bold",
        y=0.98,
    )

    # Create grid: 5 rows x 1 column
    gs = GridSpec(
        n_images,
        1,
        figure=fig,
        left=0.05,
        right=0.95,
        top=0.94,
        bottom=0.02,
        hspace=0.05,
    )

    for idx, (label, filename) in enumerate(case_info["locations"]):
        ax = fig.add_subplot(gs[idx, 0])

        # Try to load the image
        img_path = FIG_SRC / filename
        if img_path.exists():
            img = mpimg.imread(str(img_path))
            ax.imshow(img)
        else:
            ax.text(
                0.5,
                0.5,
                f"Image not found\n{filename}",
                ha="center",
                va="center",
                fontsize=10,
                transform=ax.transAxes,
            )

        # For images after the first, remove column headers by overlaying white rectangle
        if idx > 0:
            # Add white rectangle over the header area (top ~8% of image)
            rect = Rectangle(
                (0, 0.92),
                1,
                0.08,
                transform=ax.transAxes,
                facecolor="white",
                edgecolor="none",
                zorder=10,
            )
            ax.add_patch(rect)

        # For the first image, add bigger, bold column headers
        if idx == 0:
            # Calculate positions for 5 model headers
            for i, model in enumerate(MODELS):
                x_pos = (i + 0.5) / len(MODELS)
                ax.text(
                    x_pos,
                    0.96,
                    model,
                    ha="center",
                    va="center",
                    fontsize=15,
                    fontweight="bold",
                    transform=ax.transAxes,
                    zorder=11,
                )

        # Add label on the left side
        ax.text(
            -0.02,
            0.5,
            label,
            ha="right",
            va="center",
            fontsize=12,
            fontweight="bold",
            transform=ax.transAxes,
        )

        ax.axis("off")

    out_path = OUT_DIR / f"bias_strip_{case_id}.png"
    fig.savefig(out_path, dpi=180, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print(f"Saved: {out_path}")


def main():
    for case_id, case_info in CASES.items():
        make_vertical_strip(case_id, case_info)


if __name__ == "__main__":
    main()
