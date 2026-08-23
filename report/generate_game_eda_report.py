"""Generate the game-case EDA report and presentation-quality graph artifacts."""

from __future__ import annotations

import json
import re
from pathlib import Path
import sys
import textwrap
from typing import Any

import matplotlib.pyplot as plt
import networkx as nx

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from world_model_eda import WorldModelEDA


GAME_CASES = ROOT / "data" / "Test_Cases" / "03_game"
OUTPUT = ROOT / "report"
GRAPHS = OUTPUT / "game_posg_eda_graphs"
CASE_PATTERN = re.compile(r"game_G_(\d+)_.*\.md$")
TITLE_PATTERN = re.compile(r"^#{0,6}\s*Game Situation G\.\d+:\s*(.+)$", re.MULTILINE)


def load_schema(path: Path) -> dict[str, Any]:
    """Extract the first JSON object after the expected-output heading."""
    text = path.read_text(encoding="utf-8")
    expected_output = text.find("Expected LLM Output")
    if expected_output < 0:
        raise ValueError(f"{path} has no expected-output heading.")
    start = text.find("{", expected_output)
    if start < 0:
        raise ValueError(f"{path} has no JSON object after the expected-output heading.")
    return json.JSONDecoder().raw_decode(text[start:])[0]


def case_id(path: Path) -> str:
    match = CASE_PATTERN.match(path.name)
    if not match:
        raise ValueError(f"Unexpected game-case filename: {path.name}")
    return f"G{int(match.group(1))}"


def case_title(path: Path) -> str:
    """Read the human-facing game name from the case heading."""
    match = TITLE_PATTERN.search(path.read_text(encoding="utf-8"))
    if not match:
        raise ValueError(f"{path} has no game-situation title.")
    return match.group(1).strip()


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
    graph = analysis.build_state_graph()
    figure, axis = plt.subplots(figsize=(8.5, 5.6), constrained_layout=True)
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
            width=38,
            placeholder="...",
        )
        labels[state] = f"{state}\n" + "\n".join(textwrap.wrap(description, width=17))
    nx.draw_networkx_nodes(graph, positions, node_color=colors, node_size=4200, ax=axis)
    nx.draw_networkx_labels(
        graph,
        positions,
        labels=labels,
        font_color="white",
        font_weight="bold",
        font_size=6.5,
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
        -0.16,
        "Blue: initial state    Orange: terminal state    Edge labels show the action count or a single-action probability",
        transform=axis.transAxes,
        fontsize=8,
        color="#475569",
    )
    axis.set_axis_off()
    figure.savefig(GRAPHS / f"{case.lower()}_state_graph.png", dpi=220, bbox_inches="tight")
    plt.close(figure)


def save_comparison(records: list[dict[str, Any]]) -> None:
    cases = [record["case"] for record in records]
    figure, axes = plt.subplots(1, 3, figsize=(14, 4.2), constrained_layout=True)

    axes[0].bar(cases, [record["states"]["state_count"] for record in records], color="#2563eb")
    axes[0].bar(
        cases,
        [record["actions"]["joint_action_count"] for record in records],
        bottom=[record["states"]["state_count"] for record in records],
        color="#38bdf8",
    )
    axes[0].set(title="Model size and decision surface", ylabel="Count")
    axes[0].legend(["States", "Joint actions"], frameon=False)

    axes[1].bar(cases, [record["transitions"]["mean_transition_entropy"] for record in records], color="#8b5cf6")
    axes[1].set(title="Mean transition entropy", ylabel="Bits", ylim=(0, 1.7))

    axes[2].bar(cases, [record["actions"]["outcome_compression"] for record in records], color="#f97316")
    axes[2].set(title="Outcome compression", ylabel="Unique outcomes / joint actions", ylim=(0, 1.05))

    for axis in axes:
        axis.spines[["top", "right"]].set_visible(False)
        axis.grid(axis="y", alpha=0.18)
        axis.set_axisbelow(True)
    figure.suptitle("POSG game-case EDA comparison", x=0.01, ha="left", fontweight="bold")
    figure.savefig(GRAPHS / "game_case_comparison.png", dpi=220, bbox_inches="tight")
    plt.close(figure)


def render_report(records: list[dict[str, Any]]) -> str:
    rows = []
    for record in records:
        states = record["states"]
        transitions = record["transitions"]
        graph = record["graph"]
        rows.append(
            f"| {record['case']} — {record['title']} | {states['state_count']} | {states['terminal_state_count']} | "
            f"{record['actions']['joint_action_count']} | {states['mean_branching_factor']:.2f} | "
            f"{transitions['stochastic_transition_fraction']:.0%} | "
            f"{transitions['mean_transition_entropy']:.3f} | {states['maximum_trajectory_depth']} | "
            f"{graph['strongly_connected_component_count']} | {graph['average_shortest_path_length']:.2f} |"
        )
    case_reference = "\n".join(render_case_reference(record) for record in records)
    return """# Game POSG World-Model EDA

## Experiment

This report applies `WorldModelEDA` to the complete expected-output POSG schemas in the
current game benchmark. The repository currently contains **nine** game cases (G1-G9), not
ten. The analysis is descriptive: it enumerates the declared finite state/action/transition
structure and does not score whether the generated model is semantically correct.

Each case is loaded from its Markdown expected-output JSON. For every state reachable in the
declared schema, the experiment builds a directed state graph and a state-action-transition
graph, then calculates action branching, transition stochasticity and entropy, terminal
distance, and graph connectivity.

## Cross-case results

| Case and game | States | Terminal | Joint actions | Avg. branch | Stochastic | Avg. entropy (bits) | Max depth | SCCs | Avg. path |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
""" + "\n".join(rows) + """

![Cross-case comparison](game_posg_eda_graphs/game_case_comparison.png)

## Structural observations

- **One-step games dominate:** G1-G5 and G7-G9 transition directly from a single decision
  state to terminal outcomes. Their maximum terminal depth is one, and every state is its own
  strongly connected component, confirming that the schemas contain no cycles.
- **G6 is the only multi-step model:** equal bids route to a non-terminal tie-break state,
  then a stochastic Nature action selects a winner. It therefore has maximum terminal depth
  two and is the only case with a non-terminal transition after the initial joint action.
- **Stochasticity is localized:** G2 (dice duel) is stochastic at its only action; G3 is
  stochastic only for mismatched calls; and G6 is stochastic only at the tie-break. The
  remaining six cases are deterministic.
- **Outcome compression exposes action redundancy:** RPS (G1) maps nine joint actions to
  three outcomes, while Colonel Blotto (G9) maps sixteen allocations to four declared outcome
  classes. This is structural redundancy, not an error: distinct strategic choices can share
  an outcome state.
- **The report measures declared structure:** state labels collapse strategically distinct
  histories when the supplied schema uses a common outcome state. Use the state-action graph
  and reward metadata alongside this report for strategic interpretation.

## Case reference

This section links the metrics to the actual declared model. `Initial` identifies the reset
state; `terminal` identifies a state with no further decision in the schema. The terminal
distance is the shortest number of transitions from that state to any terminal state.

""" + case_reference + """

## Graph artifacts

The files below use an initial-state/terminal-state color system and aggregate parallel
state transitions into edge labels showing joint-action count and probability mass. This keeps
the diagrams readable for sharing while preserving the full action-level representation in
the EDA object.

| Case | State-transition graph |
| --- | --- |
""" + "\n".join(
    f"| {record['case']} — {record['title']} | ![{record['case']} graph](game_posg_eda_graphs/{record['case'].lower()}_state_graph.png) |"
    for record in records
) + """

## Reproduction

```powershell
python report\\generate_game_eda_report.py
python -m unittest tests.test_world_model_eda
```

`report\\generate_game_eda_report.py` discovers G1-G9 from
`data\\Test_Cases\\03_game`, extracts each expected JSON object, regenerates the PNG figures,
and overwrites this report. The analysis implementation is in `world_model_eda\\eda.py`.
"""


def render_case_reference(record: dict[str, Any]) -> str:
    """Render a human-readable schema inventory for one game."""
    schema = record["schema"]
    terminal_distances = record["terminal"]["distance_to_terminal"]
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
        joint_count = record["states"]["branching_factor_by_state"].get(state, 0)
        action_lines.append(
            f"- **`{state}`:** {player_actions}. This creates **{joint_count} joint action"
            f"{'s' if joint_count != 1 else ''}**."
        )

    reward_placement = (
        "outcome states (reward-on-arrival)"
        if any("reward" in state for state in schema["states"].values())
        else "state-action pairs"
    )
    transition_summary = transition_description(record)
    players = ", ".join(
        f"`{player['id']}`" + (f" ({player['description']})" if player.get("description") else "")
        for player in schema["players"]
    )
    return f"""### {record['case']} — {record['title']}

**Players:** {players}.
**Transition character:** {transition_summary}.
**Reward placement:** {reward_placement}.
**Structural reading:** {record['states']['state_count']} states, {record['actions']['joint_action_count']}
declared joint actions, {record['actions']['outcome_compression']:.3f} outcome compression, and
{record['graph']['strongly_connected_component_count']} strongly connected components.

| State | Role | Declared meaning | Shortest terminal distance |
| --- | --- | --- | ---: |
{chr(10).join(state_rows)}

**Available actions**
{chr(10).join(action_lines)}

"""


def transition_description(record: dict[str, Any]) -> str:
    """Summarize the deterministic/stochastic profile in plain language."""
    fraction = record["transitions"]["stochastic_transition_fraction"]
    entropy = record["transitions"]["mean_transition_entropy"]
    if fraction == 0:
        return "deterministic for every declared state-action pair"
    if fraction == 1:
        return f"stochastic for every declared state-action pair (mean entropy {entropy:.3f} bits)"
    return f"mixed: {fraction:.0%} of declared state-action pairs are stochastic (mean entropy {entropy:.3f} bits)"


def main() -> None:
    configure_style()
    GRAPHS.mkdir(parents=True, exist_ok=True)
    records = []
    for path in sorted(GAME_CASES.glob("game_G_*.md"), key=lambda item: int(CASE_PATTERN.match(item.name).group(1))):
        analysis = WorldModelEDA.from_dict(load_schema(path))
        record = {
            "case": case_id(path),
            "title": case_title(path),
            "schema": load_schema(path),
            **analysis.summary(),
        }
        records.append(record)
        save_state_graph(record["case"], record["title"], record["schema"], analysis)
    save_comparison(records)
    (OUTPUT / "game_posg_eda_report.md").write_text(render_report(records), encoding="utf-8")


if __name__ == "__main__":
    main()
