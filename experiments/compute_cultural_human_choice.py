"""Compute a human-agency metric for the cultural track, mirroring the situational
'human_action_width_max' definition, from the with-location cultural candidates.

For each candidate converted to the v2 schema we measure the maximum number of
distinct actions available to any *human* player in any non-terminal state.  This
mirrors ``exploration['human_action_width_max']`` used for the situational radar's
"Human choice represented" axis (an output counts as representing human choice when
that width exceeds 1, i.e. a human has a non-singleton choice somewhere).

Reads only the same raw transcripts the three-lane pipeline uses and does not call
any LLM or run the heavy pipeline; the aggregate is written next to the
cross-model-comparison summaries so the radar can be regenerated.
"""

from __future__ import annotations

import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "report" / "raw_output"))

import evaluate_cultural as cultural  # noqa: E402
from report.raw_output import analyze_cultural_outputs as analysis  # noqa: E402

MODELS = ("claude", "deepseek", "gpt", "llama", "qwen")
MODEL_ALIASES = {
    "opus5": "claude", "claude-opus-5": "claude",
    "gpt5-6sol": "gpt", "gpt-5.6-sol": "gpt",
    "llama3-3": "llama", "llama-3.3-70b": "llama",
    "qwen3-8": "qwen", "qwen3.8": "qwen",
    "deepseek": "deepseek",
}


def human_action_width_max(v2: dict) -> int:
    """Max distinct actions for a human player across any non-terminal state."""
    humans = {p["id"] for p in v2.get("players", []) if p.get("type") == "human"}
    width = 0
    for state in v2.get("states", []) or []:
        if state.get("terminal"):
            continue
        per_player: dict[str, list[str]] = defaultdict(list)
        for action in state.get("actions", []) or []:
            by = action.get("by", {}) or {}
            for pid in humans:
                act = by.get(pid)
                if act is not None and act not in per_player[pid]:
                    per_player[pid].append(act)
        for pid in humans:
            width = max(width, len(per_player[pid]))
    return width


def main() -> None:
    per_model: dict[str, int] = defaultdict(int)     # human_choice_outputs
    per_model_total: dict[str, int] = defaultdict(int)
    per_case: dict[tuple, int] = {}
    for (raw_model, condition), filename in analysis.TRANSCRIPTS.items():
        if condition != "with_location":
            continue
        model = MODEL_ALIASES[raw_model]
        _, blocks = analysis.parse_transcript(analysis.RAW_DIR / filename)
        for block in blocks:
            raw, _ = analysis.extract_json(block["raw"])
            if raw is None:
                continue
            try:
                v2, _ = cultural.to_v2(raw)
            except cultural.ConvertError:
                continue
            per_model_total[model] += 1
            width = human_action_width_max(v2)
            per_case[(model, block["case"])] = width
            if width > 1:
                per_model[model] += 1

    for model in MODELS:
        width = per_model.get(model, 0)
        total = per_model_total.get(model, 0)
        rate = width / total if total else 0.0
        print(f"{model:9s}  human_choice {width}/{total} = {rate:.3f}"
              f"   widths: " + " ".join(f"{c}:{per_case.get((model,c),'-')}"
                                        for c in [f"C{i}" for i in range(1, 15)]))


if __name__ == "__main__":
    main()