"""Generate a line-level root-cause report for a completed OpenRouter run."""

from __future__ import annotations

import argparse
import ast
import json
import re
from pathlib import Path
from typing import Any


MODEL_NAMES = {
    "gpt_5_6_sol": "GPT-5.6 Sol",
    "claude_opus_5": "Claude Opus 5",
    "llama_3_3_70b": "Llama 3.3 70B",
    "qwen_3_8_27b": "Qwen 3.8 27B",
    "deepseek_v4_flash": "DeepSeek V4 Flash",
}

CATEGORY_NAMES = {
    "observation_failure": "Observation-Contract Failure",
    "execution_error": "Execution Error (EDA node-type incompatibility)",
    "interface_failure": "Interface Failure (empty/truncated generation)",
    "invalid_actions": "Invalid-Actions Failure",
    "invalid_python": "Invalid-Python Failure",
}

EXECUTION_CASES = {
    ("claude_opus_5", "G9"): {
        "initial": "`initial_state()` returns the string `\"deploy\"` at generated.py:41",
        "terminal": "`transition()` returns tuple states at generated.py:57 and 60",
    },
    ("gpt_5_6_sol", "G9"): {
        "initial": "`initial_state()` returns the string `\"s0\"` at generated.py:7",
        "terminal": "`transition()` constructs a six-element tuple at generated.py:66–73 and returns it at line 74",
    },
    ("qwen_3_8_27b", "G6"): {
        "initial": "`initial_state()` returns the tuple `(\"auction\", \"low\", \"high\")` at generated.py:7",
        "terminal": "`transition()` returns string terminal states at generated.py:42, 44, and 45",
    },
}

INTERFACE_CASES = {
    ("qwen_3_8_27b", "G2"): "dice-game generation",
    ("qwen_3_8_27b", "G9"): "Colonel-Blotto generation",
}


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def artifact_dir(root: Path, row: dict[str, Any]) -> Path:
    return root / row["model"] / row["case"] / f"sample_{int(row['sample']):03d}"


def first_error_line(message: str) -> str:
    return message.splitlines()[0] if message else "No error message recorded."


def markdown_code(value: str, limit: int = 180) -> str:
    value = " ".join(value.split())
    if len(value) > limit:
        value = value[: limit - 1] + "…"
    return "`" + value.replace("`", "'") + "`"


def observation_returns(source: str) -> tuple[int, list[tuple[int, str]]]:
    tree = ast.parse(source)
    generated = next(
        node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "GeneratedPOSG"
    )
    function = next(
        node
        for node in generated.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "observation"
    )
    bad_returns = []
    for node in ast.walk(function):
        if isinstance(node, ast.Return) and isinstance(node.value, (ast.Tuple, ast.List, ast.Dict, ast.Set)):
            bad_returns.append((node.lineno, ast.unparse(node.value)))
    return function.lineno, sorted(bad_returns)


def observation_detail(row: dict[str, Any], source: str) -> list[str]:
    function_line, returns = observation_returns(source)
    refs = ", ".join(f"line {line} (`{expr}`)" for line, expr in returns)
    first_line, first_expr = returns[0]
    actual_kind = type(ast.parse(first_expr, mode="eval").body).__name__.lower()
    return [
        f"- **Failure Category:** {CATEGORY_NAMES[row['failure_type']]}",
        f"- **File & Function:** `generated.py:{function_line}`, `GeneratedPOSG.observation()`; offending returns: {refs}.",
        f"- **Error Message / Trace:** {markdown_code(first_error_line(row['error_message']))}",
        "- **Root Cause Analysis:** The rollout validator exhaustively called `observation(state, joint_action, "
        "next_state, player)` for reachable outcomes. At least one reachable branch returned a structured "
        f"{actual_kind} instead of a string. The first violating return is at generated.py:{first_line}; "
        "`rollout_world_model()` rejects it in `world_model_eda/python_posg.py:393`. This is a return-type "
        "violation, not a missing-key or player-ID error.",
        "- **Contract/Schema Difference:**",
        "  - Expected: every reachable `observation()` branch returns `str`, such as "
        "`\"outcome=win;own=rock;other=scissors\"`.",
        f"  - Actual: reachable branches return structured values; observed static return sites are {refs}.",
        "- **Recommended Fix:** Add an explicit generation rule: “`observation()` MUST return `str` on every "
        "control-flow path; tuple/list/dict/set observations are forbidden. Encode multiple fields with an "
        "f-string.” Add an AST preflight that rejects non-string literal containers returned from `observation` "
        "before rollout.",
    ]


def execution_detail(row: dict[str, Any]) -> list[str]:
    state_info = EXECUTION_CASES[(row["model"], row["case"])]
    return [
        f"- **Failure Category:** {CATEGORY_NAMES[row['failure_type']]}",
        "- **File & Function:** generated.py state constructors described below; evaluator failure at "
        "`world_model_eda/eda.py:348`, `WorldModelEDA.graph_statistics()`.",
        f"- **Error Message / Trace:** {markdown_code(row['error_message'])}",
        "- **Root Cause Analysis:** The generated class executed successfully, passed interface validation, "
        "completed exhaustive rollout, and built both graphs. Failure occurred afterward in "
        "`WorldModelEDA.summary()` → `graph_statistics()` → "
        "`networkx.community.greedy_modularity_communities()` → `MappedQueue._heapify()`. The graph contains "
        "both string and tuple node IDs. NetworkX used node IDs to break equal-priority heap ties, reached "
        "`str < tuple`, and raised `TypeError`. Therefore this is an evaluator compatibility defect exposed by "
        "a contract-permitted mixed hashable state representation, not a generated-POSG execution defect.",
        "- **Contract/Schema Difference:**",
        "  - Expected by POSG contract: any hashable state identifier; strings and tuples are both explicitly permitted.",
        f"  - Actual graph: {state_info['initial']}; {state_info['terminal']}. NetworkX's modularity routine "
        "implicitly requires mutually orderable node labels when priorities tie.",
        "- **Stack Trace Summary:** `ExperimentRunner.run_case()` → `WorldModelEDA.summary()` "
        "(`eda.py:461`) → `graph_statistics()` (`eda.py:348`) → NetworkX "
        "`greedy_modularity_communities()` → `MappedQueue`/`heapq.heapify()` → failed comparison between "
        "`str` and `tuple`.",
        "- **Recommended Fix:** Fix the evaluator by relabeling graph nodes to stable integer IDs before "
        "community detection (or pass a deterministic comparable tie-break key), while retaining original "
        "labels as attributes. As a secondary prompt guardrail, require one uniform state-ID type per generated "
        "model, but do not treat mixed hashable types as a POSG contract violation.",
    ]


def interface_detail(row: dict[str, Any]) -> list[str]:
    context = INTERFACE_CASES[(row["model"], row["case"])]
    return [
        f"- **Failure Category:** {CATEGORY_NAMES[row['failure_type']]}",
        "- **File & Function:** no `generated.py` exists; backend check at "
        "`experiments/run_openrouter_game_experiments.py:124–126`.",
        f"- **Error Message / Trace:** {markdown_code(first_error_line(row['error_message']), 260)}",
        f"- **Root Cause Analysis:** During the {context}, OpenRouter returned `finish_reason=\"length\"`, "
        "`content=null`, and 8,192 completion tokens entirely in the reasoning channel. The backend read "
        "`message.content` at line 124, found it empty, and raised `RuntimeError` at line 126. Generation "
        "therefore failed before Python parsing or `GeneratedPOSG` interface inspection; there are no missing "
        "methods or altered signatures to list.",
        "- **Contract/Schema Difference:**",
        "  - Expected: a non-empty assistant `content` string containing `class GeneratedPOSG(AbstractPOSG)` "
        "with `players`, `initial_state`, `legal_actions`, `transition`, `observation`, `reward`, and `is_terminal`.",
        "  - Actual: no code content and consequently no class or callable interface; only truncated reasoning was returned.",
        "- **Taxonomy Note:** `classify_failure()` labeled this `interface_failure` because the serialized "
        "provider payload echoed the prompt terms `GeneratedPOSG`/`AbstractPOSG`. The primary cause is output-budget "
        "exhaustion, not an interface mismatch.",
        "- **Recommended Fix:** For reasoning models, reserve a separate/larger output budget or disable reasoning "
        "for code-only generations. Treat `finish_reason=length` or `content is None` as a dedicated "
        "`generation_truncated` category and retry once with constrained reasoning and a higher content budget.",
    ]


def invalid_actions_detail(row: dict[str, Any]) -> list[str]:
    return [
        f"- **Failure Category:** {CATEGORY_NAMES[row['failure_type']]}",
        "- **File & Function:** `generated.py:14–17`, `GeneratedPOSG.legal_actions()`.",
        f"- **Error Message / Trace:** {markdown_code(first_error_line(row['error_message']))}",
        "- **Root Cause Analysis:** For reachable non-terminal state `s0_1_2`, line 17 returns `[0, 1, 2]`. "
        "The list is non-empty but its elements are integers. `rollout_world_model()` requires action identifiers "
        "to be strings and rejected both players before invoking `transition()`. No action was out of bounds; the "
        "failure is element type. There is a separate latent contract issue at generated.py:20–21: a terminal "
        "transition returns `{}`, but terminal states are not expanded by this rollout, so it did not trigger this run.",
        "- **Contract/Schema Difference:**",
        "  - Expected: non-terminal `legal_actions()` returns a non-empty `list[str]`, e.g. "
        "`[\"bid_0\", \"bid_1\", \"bid_2\"]`.",
        "  - Actual: `[0, 1, 2]` (`list[int]`) at line 17.",
        "- **Recommended Fix:** State explicitly that action IDs must be strings even when semantically numeric, "
        "and add an AST/runtime preflight asserting `all(isinstance(a, str) for a in actions)`. Also require every "
        "`transition()` branch, including terminal self-loops, to return a non-empty distribution.",
    ]


def invalid_python_detail(row: dict[str, Any]) -> list[str]:
    return [
        f"- **Failure Category:** {CATEGORY_NAMES[row['failure_type']]}",
        "- **File & Function:** `generated.py:1`; parsing occurs in `execute_generated_posg()` at "
        "`world_model_eda/python_posg.py:438`.",
        f"- **Error Message / Trace:** {markdown_code(first_error_line(row['error_message']))}",
        "- **Root Cause Analysis:** The saved response begins with three backticks followed by `python` at "
        "line 1 and has no closing fence. The backend's fence stripper only removes a complete opening/closing "
        "pair, so the raw incomplete response was saved. `ast.parse()` encountered backticks at column 1 and "
        "raised `SyntaxError` before class execution. The Python class body itself is syntactically plausible, "
        "but it was never reached. A latent semantic issue is that its stochastic transition aggregates dice "
        "outcomes into win/draw states rather than retaining individual rolls; that is not the recorded failure.",
        "- **Contract/Schema Difference:**",
        "  - Expected: raw Python beginning with `class GeneratedPOSG(AbstractPOSG):`, without Markdown fences.",
        "  - Actual: line 1 is a `python` Markdown opening fence; the response was truncated before a closing fence.",
        "- **Recommended Fix:** Reject or strip a leading fence independently of whether a closing fence exists, "
        "check `finish_reason`, and run `ast.parse()` before artifact acceptance. Retry truncated/fenced responses "
        "with “begin immediately with `class GeneratedPOSG` and never emit backticks.”",
    ]


def detail_for(row: dict[str, Any], source: str | None) -> list[str]:
    if row["failure_type"] == "observation_failure":
        if source is None:
            raise ValueError(f"Missing generated.py for observation failure {row['model']} {row['case']}")
        return observation_detail(row, source)
    if row["failure_type"] == "execution_error":
        return execution_detail(row)
    if row["failure_type"] == "interface_failure":
        return interface_detail(row)
    if row["failure_type"] == "invalid_actions":
        return invalid_actions_detail(row)
    if row["failure_type"] == "invalid_python":
        return invalid_python_detail(row)
    raise ValueError(f"Unsupported failure type: {row['failure_type']}")


def triggering_summary(row: dict[str, Any], source: str | None) -> str:
    category = row["failure_type"]
    if category == "observation_failure" and source:
        _, returns = observation_returns(source)
        line, expression = returns[0]
        return f"`observation()` returned non-string `{expression}` at generated.py:{line}"
    if category == "execution_error":
        return "NetworkX compared mixed string/tuple state IDs during modularity analysis"
    if category == "interface_failure":
        return "OpenRouter exhausted 8,192 reasoning tokens and returned `content=null`"
    if category == "invalid_actions":
        return "`legal_actions()` returned `list[int]` `[0, 1, 2]` at generated.py:17"
    return "Markdown fence at generated.py:1 caused `SyntaxError`"


def generate_report(root: Path) -> str:
    summary_path = root / "summary.json"
    rows = [row for row in load_json(summary_path) if row["status"] == "failed"]
    if len(rows) != 22:
        raise ValueError(f"Expected 22 failed cases, found {len(rows)} in {summary_path}")
    rows.sort(key=lambda row: (row["model"], int(row["case"][1:])))

    enriched = []
    for row in rows:
        case_dir = artifact_dir(root, row)
        result_path = case_dir / "result.json"
        result = load_json(result_path)
        if result["failure_type"] != row["failure_type"]:
            raise ValueError(f"Failure mismatch between summary and {result_path}")
        source_path = case_dir / "generated.py"
        source = source_path.read_text(encoding="utf-8") if source_path.exists() else None
        merged = {**row, **result, "case_dir": case_dir, "source": source}
        enriched.append(merged)

    lines = [
        "# Benchmark Failure Root-Cause Analysis",
        "",
        "Run analyzed: `openrouter-20260829T152909Z` (45 total runs; 23 passed, 22 failed).",
        "",
        "> Artifact note: this run contains no files named `validation_details.json`. The runner stored the "
        "validator diagnostics, stage statuses, and error/trace text in each `sample_001/result.json`; this report "
        "uses those records together with `summary.json`, `generated.py`, the prompt, and the evaluator source.",
        "",
        "## Summary Table",
        "",
        "| Model | Game | Failure Category | Triggering Error / Mismatch |",
        "| :--- | :--- | :--- | :--- |",
    ]
    for row in enriched:
        lines.append(
            f"| {MODEL_NAMES[row['model']]} | {row['case']} | {CATEGORY_NAMES[row['failure_type']]} | "
            f"{triggering_summary(row, row['source'])} |"
        )

    lines.extend(["", "## Detailed Case-by-Case Breakdown", ""])
    for row in enriched:
        lines.append(f"### {MODEL_NAMES[row['model']]} — Game {row['case']}")
        lines.append("")
        lines.extend(detail_for(row, row["source"]))
        lines.extend(["", "---", ""])

    lines.extend(
        [
            "## Cross-Cutting Findings and Prevention Priorities",
            "",
            "1. **Make the observation type unambiguous.** Fifteen of 22 failures are the same tuple-versus-string "
            "contract violation. Put `MUST return str on every branch` immediately beside the method signature and "
            "validate generated AST return sites before paid evaluation.",
            "2. **Separate generation failures from interface failures.** Qwen G2/G9 never produced code. Add "
            "`generation_truncated` and preserve compact provider metadata (`finish_reason`, content-token count, "
            "reasoning-token count) rather than embedding the entire provider response in `error_message`.",
            "3. **Make EDA label-agnostic.** Relabel nodes to integers before NetworkX modularity/heap algorithms. "
            "The POSG contract permits any hashable label, so evaluator metrics must not require cross-type ordering.",
            "4. **Validate syntax and interface before rollout.** Strip incomplete fences, call `ast.parse`, inspect "
            "required method signatures, and enforce `list[str]` actions with a cheap preflight.",
            "5. **Persist real tracebacks and validation details.** `result.json` currently stores flattened errors only. "
            "Add `validation_details.json` and `traceback.txt` so future reports need not reproduce evaluator exceptions.",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "run_root",
        nargs="?",
        type=Path,
        default=Path("experiments/openrouter/openrouter-20260829T152909Z"),
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    output = args.output or args.run_root / "failure_root_cause_analysis.md"
    report = generate_report(args.run_root)
    output.write_text(report, encoding="utf-8")
    print(f"Wrote {output} ({report.count('### ')} detailed cases).")


if __name__ == "__main__":
    main()
