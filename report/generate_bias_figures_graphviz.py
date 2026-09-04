#!/usr/bin/env python3
"""Render the bias-case state-graph figures (C9, C13) with Graphviz.

Replaces the earlier matplotlib/networkx rendering. Design (go-package style,
cf. https://graphviz.org/Gallery/directed/go-package.html):

  - one cluster per LLM, laid out left to right in story order:
    GPT, Llama, DeepSeek, Qwen, Opus
  - bold 18pt model name as cluster heading; 14pt state labels;
    16pt (larger) start / terminal state labels; compact spacing
  - arrowheads always visible
  - state labels wrap only at word boundaries (never mid-word)
  - edge penwidth proportional to transition probability
    (100% -> thick, 50% -> half as thick)
  - probability labels are attached to their edge (never floating)

Output: overleaf/figures/bias_C9.png, overleaf/figures/bias_C13.png
(copied to overleaf/fig/ for name.tex as well)

    python report/generate_bias_figures_graphviz.py
"""
from __future__ import annotations

import json
import os
import shutil
import sys
import textwrap
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "report" / "raw_output"))

import evaluate_cultural as ec  # noqa: E402
import analyze_cultural_outputs as ac  # noqa: E402

FIG_DIRS = [ROOT / "overleaf" / "figures", ROOT / "overleaf" / "fig"]
CASES = ["C9", "C13"]
FONT = "Helvetica,Arial,sans-serif"
# Story order left -> right (display name, transcript key)
MODELS = [("GPT", "gpt5-6sol"), ("Llama", "llama3-3"), ("DeepSeek", "deepseek"),
          ("Qwen", "qwen3-8"), ("Opus", "opus5")]
NODE_COLORS = {"normal": ("#c9c9c9", "#555555", "black"),
               "terminal": ("#3b7dd8", "#1d4f9e", "white"),
               "init": ("#f59e0b", "#b36b00", "black")}


def ensure_dot_on_path() -> None:
    if shutil.which("dot"):
        return
    cand = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Graphviz" / "bin"
    if (cand / "dot.exe").exists():
        os.environ["PATH"] = str(cand) + os.pathsep + os.environ.get("PATH", "")
        return
    raise RuntimeError("Graphviz 'dot' executable not found; install Graphviz first.")


def wrap_name(name: str, width: int = 12, max_lines: int = 3) -> str:
    """Wrap a state name only at word boundaries (underscores become spaces)."""
    name = name.replace("_", " ").replace("-", " ").strip()
    lines = textwrap.wrap(name, width=width, break_long_words=False,
                          break_on_hyphens=False)
    if len(lines) > max_lines:  # keep full words, join the tail
        lines = lines[:max_lines - 1] + [" ".join(lines[max_lines - 1:])]
    return "\n".join(lines)


def prob_label(probs: list[float]) -> str:
    return "/".join(("1" if p == 1.0 else "0" if p == 0.0
                     else f"{p:.2f}".rstrip("0").rstrip(".")) for p in probs)


def collect_edges(v2: dict) -> dict:
    """(u, v) -> list of transition probabilities."""
    edges: dict = {}
    for st in v2["states"]:
        for action in st.get("actions", []):
            for e in action.get("next", []):
                edges.setdefault((st["id"], e["state"]), []).append(e["p"])
    return edges


def render_case(cid: str) -> Path:
    import graphviz

    g = graphviz.Digraph(cid, format="png")
    g.attr("graph", rankdir="LR", ranksep="0.45", nodesep="0.28",
           fontname=FONT, bgcolor="white", newrank="true", compound="true",
           splines="spline", dpi="150")
    g.attr("node", fontname=FONT, fontsize="14", shape="ellipse",
           style="filled", margin="0.04,0.02")
    g.attr("edge", fontname=FONT, fontsize="11", color="#7a7a7a",
           arrowsize="0.8", fontcolor="#333333")

    init_nodes, sink_nodes = [], []
    for i, (disp, key) in enumerate(MODELS):
        path = ac.RAW_DIR / ac.TRANSCRIPTS[(key, "with_location")]
        _, blocks = ac.parse_transcript(path)
        block = next(b for b in blocks if b["case"] == cid)
        model_json, _ = ac.extract_json(block["raw"])
        with g.subgraph(name=f"cluster_{i}") as c:
            c.attr(label=f"<B>{disp}</B>", labelloc="t", fontsize="18",
                   fontname=FONT, style="rounded", color="#bbbbbb", penwidth="1.0",
                   margin="10")
            if model_json is None:
                c.node(f"none_{i}", "no output recovered", fillcolor="#d6d6d6",
                       color="#999999", fontsize="14")
                init_nodes.append(f"none_{i}")
                sink_nodes.append(f"none_{i}")
                continue
            v2, _ = ec.to_v2(json.loads(json.dumps(model_json)))
            states = {s["id"]: s for s in v2["states"]}
            init = {n["state"] if isinstance(n, dict) else n for n in v2["initial"]}
            terminal = {s for s in states if states[s].get("terminal")} - init
            for sid in sorted(states):
                kind = ("init" if sid in init else
                        "terminal" if sid in terminal else "normal")
                fill, border, fcolor = NODE_COLORS[kind]
                c.node(sid, label=wrap_name(sid),
                       fillcolor=fill, color=border, fontcolor=fcolor,
                       fontsize="16" if kind in ("init", "terminal") else "14",
                       penwidth="1.4" if kind != "normal" else "1.0")
            for (u, v), probs in collect_edges(v2).items():
                p_mean = sum(probs) / len(probs)
                stochastic = len(probs) > 1 or any(abs(p - 1.0) > 1e-9 for p in probs)
                attrs = {"penwidth": f"{max(0.8, 4.0 * p_mean):.2f}",
                         "arrowsize": f"{0.6 + 0.6 * p_mean:.2f}"}
                if stochastic:
                    attrs["label"] = prob_label(probs)
                g.edge(u, v, **attrs)
            init_nodes.append(min(init) if init else sorted(states)[0])
            sink_nodes.append(sorted(terminal)[-1] if terminal else sorted(states)[-1])

    # invisible high-weight chain: forces cluster order GPT -> Llama -> DeepSeek
    # -> Qwen -> Opus from left to right
    for a, b in zip(sink_nodes, init_nodes[1:]):
        g.edge(a, b, style="invis", weight="50", constraint="true")

    out = FIG_DIRS[0] / f"bias_{cid}"
    g.render(outfile=f"bias_{cid}.png", directory=str(FIG_DIRS[0]), cleanup=True)
    for d in FIG_DIRS[1:]:
        shutil.copy2(FIG_DIRS[0] / f"bias_{cid}.png", d / f"bias_{cid}.png")
    return out.with_suffix(".png")


def main() -> None:
    ensure_dot_on_path()
    for d in FIG_DIRS:
        d.mkdir(parents=True, exist_ok=True)
    for cid in CASES:
        print(f"wrote {render_case(cid)}")


if __name__ == "__main__":
    main()