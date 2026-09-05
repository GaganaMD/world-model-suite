"""Create dependency-free SVG visualizations for the five-model comparison.

The plots use only persisted CSV files, so they run on a CPU without re-executing any
generated model. Radar axes are normalized rates or F1 scores in [0, 1].
"""
from __future__ import annotations

import csv
import html
import math
from collections import defaultdict
from pathlib import Path
from statistics import mean

import numpy as np
from matplotlib import pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "results" / "cross_model_comparison"
OUT = DATA / "figures"
MODELS = ("claude", "deepseek", "gpt", "llama", "qwen")
COLORS = {"claude": "#4c78a8", "deepseek": "#f58518", "gpt": "#54a24b",
          "llama": "#e45756", "qwen": "#9467bd"}


def read(name: str) -> list[dict[str, str]]:
    with (DATA / name).open(encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def esc(value: object) -> str:
    return html.escape(str(value))


def save(name: str, body: str, width: int, height: int) -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
           f'viewBox="0 0 {width} {height}"><rect width="100%" height="100%" fill="white"/>'
           f'<style>text{{font-family:Arial,sans-serif;fill:#222}} .grid{{stroke:#bbb;fill:none}}</style>'
           f'{body}</svg>')
    (OUT / name).write_text(svg, encoding="utf-8")


def radar(name: str, title: str, axes: list[str], series: dict[str, list[float]]) -> None:
    width, height, cx, cy, radius = 920, 650, 440, 315, 220
    count = len(axes)
    points = [(cx + radius * math.sin(2 * math.pi * i / count),
               cy - radius * math.cos(2 * math.pi * i / count)) for i in range(count)]
    body = f'<text x="{cx}" y="32" text-anchor="middle" font-size="22" font-weight="bold">{esc(title)}</text>'
    for level in (.2, .4, .6, .8, 1.0):
        ring = " ".join(f"{cx+(x-cx)*level:.1f},{cy+(y-cy)*level:.1f}" for x, y in points)
        body += f'<polygon class="grid" points="{ring}"/><text x="{cx+5}" y="{cy-radius*level+14}" font-size="11">{level:.1f}</text>'
    for (x, y), label in zip(points, axes):
        body += f'<line class="grid" x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}"/>'
        lx, ly = cx + (x-cx)*1.16, cy + (y-cy)*1.16
        anchor = "middle" if abs(lx-cx) < 25 else ("start" if lx > cx else "end")
        body += f'<text x="{lx:.1f}" y="{ly:.1f}" text-anchor="{anchor}" font-size="13">{esc(label)}</text>'
    for index, (label, values) in enumerate(series.items()):
        coordinates = " ".join(
            f"{cx+(points[i][0]-cx)*max(0,min(1,value)):.1f},{cy+(points[i][1]-cy)*max(0,min(1,value)):.1f}"
            for i, value in enumerate(values)
        )
        color = COLORS[label]
        body += f'<polygon points="{coordinates}" fill="{color}" fill-opacity="0.10" stroke="{color}" stroke-width="2"/>'
        body += f'<rect x="{735}" y="{105+index*28}" width="18" height="12" fill="{color}"/><text x="760" y="{116+index*28}" font-size="13">{esc(label)}</text>'
    body += '<text x="20" y="635" font-size="11">All axes range from 0 (center) to 1 (outer ring). Structural agreement is feature-multiset F1.</text>'
    save(name, body, width, height)


def situational_radar() -> None:
    models = [row for row in read("summary_by_model.csv") if row["domain"] == "situational"]
    pairs = [row for row in read("summary_by_model_pair.csv") if row["domain"] == "situational"]
    agreement = defaultdict(list)
    for row in pairs:
        if row["mean_structural_f1"]:
            value = float(row["mean_structural_f1"])
            agreement[row["model_a"]].append(value); agreement[row["model_b"]].append(value)
    series = {}
    for row in models:
        model = row["model"]
        series[model] = [float(row["validity_rate"]), float(row["mean_criteria_coverage_proxy"]),
                         int(row["human_choice_outputs"])/int(row["outputs"]), mean(agreement[model])]
    radar("situational_model_radar.svg", "Situational model comparison",
          ["Mechanical validity", "Stakeholder capacity", "Human choice represented", "Pairwise structural agreement"], series)


def cultural_radar() -> None:
    models = [row for row in read("summary_by_model.csv") if row["domain"] == "cultural"]
    pairs = [row for row in read("summary_by_model_pair.csv") if row["domain"] == "cultural"]
    agreement = defaultdict(list)
    for row in pairs:
        if row["mean_structural_f1"]:
            value = float(row["mean_structural_f1"])
            agreement[row["model_a"]].append(value); agreement[row["model_b"]].append(value)
    series = {}
    for row in models:
        model = row["model"]
        series[model] = [float(row["validity_rate"]), float(row["mean_criteria_coverage_proxy"]),
                         int(row["human_choice_outputs"])/int(row["outputs"]), mean(agreement[model])]
    radar("cultural_model_radar.svg", "Cultural model comparison",
          ["Mechanical validity", "Semantic coverage", "Human choice represented", "Pairwise structural agreement"], series)


def cross_domain_radar() -> None:
    rows = read("summary_by_model.csv"); pairs = read("summary_by_model_pair.csv")
    validity = {(r["domain"], r["model"]): float(r["validity_rate"]) for r in rows}
    agreement = defaultdict(list)
    for row in pairs:
        if row["mean_structural_f1"]:
            value = float(row["mean_structural_f1"])
            for model in (row["model_a"], row["model_b"]): agreement[(row["domain"], model)].append(value)
    series = {model: [validity[(domain, model)] for domain in ("situational", "cultural", "game")]
                       + [mean(agreement[(domain, model)]) for domain in ("situational", "cultural", "game")]
              for model in MODELS}
    radar("cross_domain_model_radar.svg", "Five-model comparison across domains",
          ["S validity", "C validity", "G validity", "S agreement", "C agreement", "G agreement"], series)


def heatmaps() -> None:
    rows = read("summary_by_model_pair.csv"); cell, margin = 86, 155
    for domain in ("situational", "cultural", "game"):
        values = {}
        for row in rows:
            if row["domain"] == domain and row["mean_structural_f1"]:
                values[frozenset((row["model_a"], row["model_b"]))] = float(row["mean_structural_f1"])
        body = f'<text x="{margin+cell*2.5}" y="30" text-anchor="middle" font-size="20" font-weight="bold">{domain.title()} pairwise structural agreement</text>'
        for i, model in enumerate(MODELS):
            body += f'<text x="{margin-10}" y="{75+i*cell+cell/2}" text-anchor="end" font-size="13">{model}</text>'
            body += f'<text x="{margin+i*cell+cell/2}" y="60" text-anchor="middle" font-size="13">{model}</text>'
            for j, other in enumerate(MODELS):
                value = 1.0 if i == j else values.get(frozenset((model, other)))
                if value is None:
                    color, label = "#eeeeee", "N/A"
                else:
                    red, green = int(235*(1-value)+40), int(70+150*value)
                    color, label = f"rgb({red},{green},105)", f"{value:.2f}"
                x, y = margin+j*cell, 75+i*cell
                body += f'<rect x="{x}" y="{y}" width="{cell}" height="{cell}" fill="{color}" stroke="white"/>'
                body += f'<text x="{x+cell/2}" y="{y+cell/2+5}" text-anchor="middle" font-size="14">{label}</text>'
        save(f"{domain}_pairwise_heatmap.svg", body, 650, 540)


def divergence_chart() -> None:
    rows = read("scenario_agreement.csv")
    grouped = defaultdict(list)
    for row in rows:
        if row["mean_pairwise_structural_f1"]:
            grouped[(row["domain"], row["case"])].append(float(row["mean_pairwise_structural_f1"]))
    items = sorted(((domain, case, mean(values)) for (domain, case), values in grouped.items()),
                   key=lambda item: (item[0], item[2]))
    width, height, left, top, row_h = 900, 1120, 190, 50, 29
    body = '<text x="450" y="28" text-anchor="middle" font-size="21" font-weight="bold">Within-scenario structural agreement</text>'
    domain_colors = {"situational":"#4c78a8", "cultural":"#f58518", "game":"#54a24b"}
    for i, (domain, case, value) in enumerate(items):
        y = top+i*row_h
        body += f'<text x="{left-10}" y="{y+15}" text-anchor="end" font-size="12">{domain[0].upper()} / {case}</text>'
        body += f'<rect x="{left}" y="{y}" width="{value*620:.1f}" height="19" fill="{domain_colors[domain]}"/>'
        body += f'<text x="{left+value*620+6:.1f}" y="{y+15}" font-size="11">{value:.3f}</text>'
    body += '<text x="500" y="1100" text-anchor="middle" font-size="12">Mean pairwise structural F1 (higher means more similar structure)</text>'
    save("scenario_agreement_bars.svg", body, width, height)


def fallback_f1_heatmaps() -> None:
    """Write three square PNG heatmaps of the fallback structural-feature F1 matrix."""
    rows = read("summary_by_model_pair.csv")
    values = {}
    for row in rows:
        if row["mean_structural_f1"]:
            values[(row["domain"], frozenset((row["model_a"], row["model_b"])))] = float(row["mean_structural_f1"])
    for domain in ("cultural", "situational", "game"):
        matrix = np.ones((len(MODELS), len(MODELS)))
        for i, left in enumerate(MODELS):
            for j, right in enumerate(MODELS):
                if i != j:
                    matrix[i, j] = values.get((domain, frozenset((left, right))), np.nan)
        fig, ax = plt.subplots(figsize=(5.6, 5.6))
        masked = np.ma.masked_invalid(matrix)
        ax.imshow(masked, cmap="viridis", vmin=0.0, vmax=1.0)
        ax.set_aspect("equal")
        ax.set_xticks(range(len(MODELS))); ax.set_xticklabels(MODELS, fontsize=13)
        ax.set_yticks(range(len(MODELS))); ax.set_yticklabels(MODELS, fontsize=13)
        for i in range(len(MODELS)):
            for j in range(len(MODELS)):
                if not np.isnan(matrix[i, j]):
                    ax.text(j, i, f"{matrix[i, j]:.2f}", ha="center", va="center",
                            color="white" if matrix[i, j] < 0.55 else "black", fontsize=13)
        fig.savefig(OUT / f"{domain}_fallback_structural_feature_f1_heatmap.png",
                    dpi=200, bbox_inches="tight")
        plt.close(fig)


def main() -> None:
    situational_radar(); cultural_radar(); cross_domain_radar(); heatmaps(); divergence_chart()
    fallback_f1_heatmaps()
    print(f"Wrote 7 SVG figures + 3 PNG heatmaps to {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
