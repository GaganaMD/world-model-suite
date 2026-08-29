"""Generate the cultural-case EDA report and presentation-quality graph artifacts.

Mirrors ``generate_game_eda_report.py`` for the 14 cultural-track reference world
models (C1-C14, authored in ``generate_cultural_references.py``). Because the
cultural track has no canonical expected-output JSON inside the .md files, the
reference models in ``data/Test_Cases/04_cultural/reference_models.json`` play
the role of the game track's expected-output schemas.

In addition to the per-case state graphs and the cross-case bar comparison used
for G1-G9, this generator adds **heatmaps**: a cross-case metric heatmap
(cases x normalized EDA descriptors) and per-case transition-probability
heatmaps (source state x target state, probability mass aggregated over all
joint actions).

    python report\\generate_cultural_eda_report.py
"""
from __future__ import annotations

import json
import re
import sys
import textwrap
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from world_model_eda import WorldModelEDA  # noqa: E402

CULTURAL_CASES = ROOT / "data" / "Test_Cases" / "04_cultural"
REFERENCES = CULTURAL_CASES / "reference_models.json"
OUTPUT = ROOT / "report"
GRAPHS = OUTPUT / "cultural_eda_graphs"
REPORT = OUTPUT / "cultural_eda_report.md"
TITLE_PATTERN = re.compile(
    r"^#{0,6}\s*Test Case\s+C\.\d+\s*\(([^)]*?)\)\s*:\s*(.+)$", re.MULTILINE
)


def load_references() -> dict[str, Any]:
    payload = json.loads(REFERENCES.read_text(encoding="utf-8"))
    return payload["references"]


def parse_case_meta(path: Path):
    """-> (country, title) using the same parser as evaluate_cultural.py."""
    from evaluate_cultural import parse_case

    try:
        parsed = parse_case(path)
        return parsed.country, parsed.title
    except Exception:  # noqa: BLE001 - fall back to the file heading regex
        text = path.read_text(encoding="utf-8")
        match = TITLE_PATTERN.search(text)
        if match:
            return match.group(1).strip(), match.group(2).strip()
        return "", path.stem


def configure_style() -> None:
    plt.rcParams.update(
        {
            "figure.facecolor": "#f8fafc",
            "axes.facecolor": "#f8fafc",
            "axes.edgecolor": "#cbd5e1",
            "axes.labelcolor": "#1e293b",
            "axes.titleweight": "bold",
            "font.family": "DejaVu Sans",
            "text.color": "#1e293b",
            "xtick.color": "#475569",
            "ytick.color": "#475569",
        }
    )


def save_state_graph(case: str, title: str, schema: dict[str, Any], analysis: WorldModelEDA) -> None:
    """State-transition graph with initial/terminal colour coding (same as the game report)."""
    graph = analysis.build_state_graph()
    figure, axis = plt.subplots(figsize=(9.5, 5.8), constrained_layout=True)
    initial = analysis.initial_state
    terminals = sorted(analysis.terminal_states, key=repr)
    positions = {initial: (0, 1)} if initial in graph else {}
    positions.update({state: (index, 0) for index, state in enumerate(terminals)})
    for index, state in enumerate(node for node in graph if node not in positions):
        positions[state] = (index, 0.5)

    colors = [
        "#2563eb" if state == initial else "#f97316" if state in analysis.terminal_states else "#64748b"
        for state in graph
    ]
    labels = {}
    for state in graph:
        description = textwrap.shorten(
            schema["states"][state].get("description", ""),
            width=42,
            placeholder="...",
        )
        labels[state] = f"{state}\n" + "\n".join(textwrap.wrap(description, width=19))
    nx.draw_networkx_nodes(graph, positions, node_color=colors, node_size=4600, ax=axis)
    nx.draw_networkx_labels(
        graph,
        positions,
        labels=labels,
        font_color="white",
        font_weight="bold",
        font_size=7.0,
        ax=axis,
    )
    nx.draw_networkx_edges(
        graph,
        positions,
        edge_color="#94a3b8",
        arrowsize=20,
        width=1.8,
        connectionstyle="arc3,rad=0.08",
        ax=axis,
    )
    edge_labels = {
        (source, target): (
            f"{len(data['actions'])} joint actions"
            if len(data["actions"]) != 1
            else f"1 joint action\np={data['probability']:.3g}"
        )
        for source, target, data in graph.edges(data=True)
    }
    nx.draw_networkx_edge_labels(
        graph, positions, edge_labels=edge_labels, font_size=8, rotate=False, ax=axis
    )
    axis.set_title(f"{case} — {title}", loc="left", pad=12)
    axis.text(
        0,
        -0.14,
        "Blue: initial state    Orange: terminal state    Edge labels show the action count or a single-action probability",
        transform=axis.transAxes,
        fontsize=8,
        color="#475569",
    )
    axis.set_axis_off()
    figure.savefig(GRAPHS / f"{case.lower()}_state_graph.png", dpi=220, bbox_inches="tight")
    plt.close(figure)

def metric_rows(records: list[dict[str, Any]]) -> list[tuple[str, str, float]]:
    """Flattened (case, metric, value) triples for the cross-case heatmap."""
    rows = []
    for record in records:
        cid = record["case"]
        s = record["eda"]["states"]
        a = record["eda"]["actions"]
        t = record["eda"]["transitions"]
        g = record["eda"]["graph"]
        rows.extend(
            [
                (cid, "states", s["state_count"]),
                (cid, "terminal", s["terminal_state_count"]),
                (cid, "joint_actions", a["joint_action_count"]),
                (cid, "mean_branch", s["mean_branching_factor"] or 0.0),
                (cid, "stochastic_frac", t["stochastic_transition_fraction"]),
                (cid, "mean_entropy", t["mean_transition_entropy"] or 0.0),
                (cid, "max_depth", s["maximum_trajectory_depth"] or 0),
                (cid, "sccs", g["strongly_connected_component_count"]),
                (cid, "avg_path", g["average_shortest_path_length"] or 0.0),
            ]
        )
    return rows


def save_cross_case_heatmap(records: list[dict[str, Any]]) -> None:
    """Cases x metrics heatmap with per-column min-max colour scaling."""
    import numpy as np

    rows = metric_rows(records)
    cases = [record["case"] for record in records]
    metrics = sorted({metric for _, metric, _ in rows})
    matrix = np.full((len(cases), len(metrics)), np.nan)
    for cid, metric, value in rows:
        matrix[cases.index(cid), metrics.index(metric)] = value

    norm = np.full_like(matrix, np.nan)
    for col in range(matrix.shape[1]):
        column = matrix[:, col]
        lo, hi = float(np.nanmin(column)), float(np.nanmax(column))
        if hi > lo:
            norm[:, col] = (column - lo) / (hi - lo)

    figure, axis = plt.subplots(figsize=(11.5, 6.2), constrained_layout=True)
    image = axis.imshow(norm, cmap="YlGnBu", aspect="auto", vmin=0, vmax=1)
    axis.set_xticks(range(len(metrics)), [m.replace("_", " ") for m in metrics], rotation=30, ha="right")
    axis.set_yticks(range(len(cases)), cases)
    for row in range(len(cases)):
        for col in range(len(metrics)):
            value = matrix[row, col]
            if np.isnan(value):
                continue
            display = f"{value:.2f}".rstrip("0").rstrip(".") if value != int(value) else f"{int(value)}"
            axis.text(
                col, row,
                display,
                ha="center", va="center", fontsize=8,
                color="#0f172a" if 0.35 < norm[row, col] < 0.75 else "white",
            )
    axis.set_title("Cultural reference models — cross-case metric heatmap (per-column min-max scale)", pad=10)
    figure.colorbar(image, ax=axis, shrink=0.8, label="scaled intensity")
    figure.savefig(GRAPHS / "cultural_case_metrics_heatmap.png", dpi=220, bbox_inches="tight")
    plt.close(figure)
def save_transition_heatmaps(records: list[dict[str, Any]]) -> None:
    """One probability heatmap per case: source state (rows) x target state (columns)."""
    import numpy as np

    count = len(records)
    columns = 3
    rows_count = (count + columns - 1) // columns
    figure, axes = plt.subplots(rows_count, columns, figsize=(4.4 * columns, 3.4 * rows_count),
                                constrained_layout=True)
    axes_flat = axes.ravel()
    for index, record in enumerate(records):
        axis = axes_flat[index]
        decl = record["declarative"]
        states = list(decl["states"])
        table = np.zeros((len(states), len(states)))
        for source, outcomes in (decl.get("transition_probabilities") or {}).items():
            if source not in states:
                continue
            for next_state, probability in outcomes.items():
                if next_state not in states:
                    continue
                table[states.index(source), states.index(next_state)] += float(probability)
        image = axis.imshow(table, cmap="viridis", vmin=0, vmax=1)
        axis.set_xticks(range(len(states)), states, rotation=45, ha="right", fontsize=6)
        axis.set_yticks(range(len(states)), states, fontsize=6)
        axis.set_title(record["case"], fontsize=9)
    for index in range(len(records), len(axes_flat)):
        axes_flat[index].axis("off")
    figure.suptitle("Cultural reference models — transition-probability heatmaps (rows: source, columns: target)",
                    fontweight="bold", y=1.0)
    figure.colorbar(image, ax=axes_flat, shrink=0.6, label="probability")
    figure.savefig(GRAPHS / "cultural_transition_heatmaps.png", dpi=220, bbox_inches="tight")
    plt.close(figure)


def save_comparison(records: list[dict[str, Any]]) -> None:
    """Bar comparison figure (mirrors the game-track figure for continuity)."""
    cases = [record["case"] for record in records]
    figure, axes = plt.subplots(1, 3, figsize=(14, 4.2), constrained_layout=True)

    axes[0].bar(cases, [record["eda"]["states"]["state_count"] for record in records], color="#2563eb")
    axes[0].bar(
        cases,
        [record["eda"]["actions"]["joint_action_count"] for record in records],
        bottom=[record["eda"]["states"]["state_count"] for record in records],
        color="#38bdf8",
    )
    axes[0].set(title="Model size and decision surface", ylabel="Count")
    axes[0].legend(["States", "Joint actions"], frameon=False)

    axes[1].bar(cases, [record["eda"]["transitions"]["mean_transition_entropy"] for record in records], color="#8b5cf6")
    axes[1].set(title="Mean transition entropy", ylabel="Bits", ylim=(0, 1.05))

    axes[2].bar(cases, [record["eda"]["actions"]["outcome_compression"] for record in records], color="#f97316")
    axes[2].set(title="Outcome compression", ylabel="Unique outcomes / joint actions", ylim=(0, 1.05))

    for axis in axes:
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(axis="y", alpha=0.18)
        axis.set_axisbelow(True)
    figure.suptitle("Cultural-case EDA comparison (reference models C1-C14)", x=0.01, ha="left", fontweight="bold")
    figure.savefig(GRAPHS / "cultural_case_comparison.png", dpi=220, bbox_inches="tight")
    plt.close(figure)
def transition_description(record: dict[str, Any]) -> str:
    fraction = record["eda"]["transitions"]["stochastic_transition_fraction"]
    entropy = record["eda"]["transitions"]["mean_transition_entropy"]
    if fraction == 0:
        return "deterministic for every declared state-action pair"
    if fraction == 1:
        return f"stochastic for every declared state-action pair (mean entropy {entropy:.3f} bits)"
    return f"mixed: {fraction:.0%} of declared state-action pairs are stochastic (mean entropy {entropy:.3f} bits)"


def render_case_reference(record: dict[str, Any]) -> str:
    schema = record["declarative"]
    terminal_distances = record["eda"]["terminal"]["distance_to_terminal"]
    state_rows = []
    for state, metadata in schema["states"].items():
        role = []
        if state == schema["initial_state"]:
            role.append("initial")
        if metadata.get("terminal", False):
            role.append("terminal")
        elif not role:
            role.append("decision")
        state_rows.append(
            f"| `{state}` | {', '.join(role)} | {metadata.get('description', 'No description supplied.')} | "
            f"{terminal_distances[state]} |"
        )

    action_lines = []
    for state, players in schema.get("actions", {}).items():
        player_actions = "; ".join(
            f"`{player}`: {', '.join(f'`{action}`' for action in actions)}"
            for player, actions in players.items()
        )
        joint_count = record["eda"]["states"]["branching_factor_by_state"].get(state, 0)
        action_lines.append(
            f"- **`{state}`:** {player_actions}. This creates **{joint_count} joint action"
            f"{'s' if joint_count != 1 else ''}**."
        )

    players = ", ".join(
        f"`{player['id']}`" + (f" ({player['description']})" if player.get("description") else "")
        for player in schema["players"]
    )
    st = record["eda"]["states"]
    ac = record["eda"]["actions"]
    gr = record["eda"]["graph"]
    return f"""### {record['case']} — {record['title']}

**Country:** {record['country']}.
**Players:** {players}.
**Transition character:** {transition_description(record)}.
**Structural reading:** {st['state_count']} states, {ac['joint_action_count']}
declared joint actions, {ac['outcome_compression']:.3f} outcome compression, and
{gr['strongly_connected_component_count']} strongly connected components.

| State | Role | Declared meaning | Shortest terminal distance |
| --- | --- | --- | ---: |
{chr(10).join(state_rows)}

**Available actions**
{chr(10).join(action_lines)}

"""
def render_report(records: list[dict[str, Any]]) -> str:
    rows = []
    for record in records:
        s = record["eda"]["states"]
        a = record["eda"]["actions"]
        t = record["eda"]["transitions"]
        g = record["eda"]["graph"]
        rows.append(
            f"| {record['case']} — {record['title']} | {s['state_count']} | {s['terminal_state_count']} | "
            f"{a['joint_action_count']} | {s['mean_branching_factor']:.2f} | "
            f"{t['stochastic_transition_fraction']:.0%} | "
            f"{t['mean_transition_entropy']:.3f} | {s['maximum_trajectory_depth']} | "
            f"{g['strongly_connected_component_count']} | {g['average_shortest_path_length']:.2f} |"
        )
    case_reference = "\n".join(render_case_reference(record) for record in records)
    return """# Cultural POSG World-Model EDA (C1-C14)

## Experiment

This report applies `WorldModelEDA` to the **reference world models** of the cultural
track, the direct counterpart of the game-track EDA report. The game track carries an
expected-output POSG inside every case .md; the cultural track is open-ended
(expect/avoid), so its expected models are authored in
`report/generate_cultural_references.py` and stored in
`data/Test_Cases/04_cultural/reference_models.json`. Each reference deliberately
embodies the case's "should include" criteria and passes Lane 1 after v1->v2
conversion.

For every state reachable in the declared schema, the experiment builds a directed
state graph and a state-action-transition graph, then calculates action branching,
transition stochasticity and entropy, terminal distance, and graph connectivity.
Two heatmap families are added: a **cross-case metric heatmap** (cases x normalized
EDA descriptors) and **per-case transition-probability heatmaps** (source x target
state, probability mass aggregated over all joint actions).

## Cross-case results

| Case and title | States | Terminal | Joint actions | Avg. branch | Stochastic | Avg. entropy (bits) | Max depth | SCCs | Avg. path |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
""" + "\n".join(rows) + """

![Cross-case comparison](cultural_eda_graphs/cultural_case_comparison.png)

![Cross-case metric heatmap](cultural_eda_graphs/cultural_case_metrics_heatmap.png)

![Per-case transition heatmaps](cultural_eda_graphs/cultural_transition_heatmaps.png)

## Structural observations

- **Uniformly small, one-step models.** Every reference is a single decision state
  (the robot) with four alternative actions routing to terminal outcomes except C1,
  which has two decision states (verify first, then choose how to handle the
  correction). Maximum trajectory depth is one for all but C1, and every state is
  its own strongly connected component.
- **Deterministic by design.** The references declare 1.0 probabilities throughout;
  the stochasticity and entropy columns are all zero. This is a modelling choice for
  the cultural track: the *judgment* (which action is appropriate) is the open part,
  not the transition dynamics.
- **Outcome compression is maximal.** Four actions each map to a distinct terminal
  state in most cases, so outcome compression is 1.000 — the reference models make no
  outcome-sharing simplifications.
- **Same structure, different norms.** C1-C14 share a common skeleton (3-4
  stakeholders, 1-2 decision states, 4 actions) yet encode different social stakes;
  the EDA numbers therefore describe *structural* uniformity, while the per-case
  narrative and Lane-3 checklist carry the cultural content.

## Case reference

This section links the metrics to the actual declared model. `Initial` identifies
the reset state; `terminal` identifies a state with no further decision in the
schema. The terminal distance is the shortest number of transitions from that state
to any terminal state.

""" + case_reference + """

## Graph artifacts

The files below use an initial-state/terminal-state colour system and aggregate
parallel state transitions into edge labels showing joint-action count and
probability mass.

| Case | State-transition graph |
| --- | --- |
""" + "\n".join(
    f"| {record['case']} — {record['title']} | ![{record['case']} graph](cultural_eda_graphs/{record['case'].lower()}_state_graph.png) |"
    for record in records
) + """

## Reproduction

```powershell
python report\\generate_cultural_references.py     # author C1-C14 reference models
python report\\generate_cultural_eda_report.py     # build this report + graphs
python -m unittest tests.test_world_model_eda
```

`report\\generate_cultural_eda_report.py` discovers C1-C14 from
`data\\Test_Cases\\04_cultural\\reference_models.json`, runs `WorldModelEDA` on each,
regenerates the PNG figures, and overwrites this report.
"""


def main() -> None:
    configure_style()
    GRAPHS.mkdir(parents=True, exist_ok=True)
    references = load_references()
    records = []
    for cid in sorted(references, key=lambda item: int(item[1:])):
        schema = references[cid]
        analysis = WorldModelEDA.from_dict(schema)
        case_path = CULTURAL_CASES / f"cultural_C_{cid[1:]}_Test_Case_C{cid[1:]}.md"
        country, title = (cid, cid)
        if case_path.exists():
            country, title = parse_case_meta(case_path)
        record = {
            "case": cid,
            "title": title,
            "country": country,
            "declarative": schema,
            "eda": analysis.summary(),
        }
        records.append(record)
        save_state_graph(record["case"], record["title"], record["declarative"], analysis)
    save_comparison(records)
    save_cross_case_heatmap(records)
    save_transition_heatmaps(records)
    REPORT.write_text(render_report(records), encoding="utf-8")
    print(f"report written: {REPORT}")


if __name__ == "__main__":
    main()
