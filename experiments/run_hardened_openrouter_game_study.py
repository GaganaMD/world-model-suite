"""Hardened OpenRouter study for the nine game POSG cases.

The runner keeps prompts, untouched replies, extracted Python, probe reports,
canonical world-model JSON, optional ``.pth`` graph tensors, and a run summary
under one timestamped directory. Generated code is checked in a time-limited
subprocess and mechanically invalid attempts can be repaired by the same model.
"""

from __future__ import annotations

import argparse
import ast
import contextlib
import csv
import io
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping

import requests


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from world_model_eda.eda import WorldModelEDA
from world_model_eda.python_posg import (
    build_state_graph,
    canonical_rollout_json,
    execute_generated_posg,
    rollout_world_model,
)


CASE_ROOT = REPO_ROOT / "data" / "Test_Cases" / "03_game"
OUTPUT_ROOT = REPO_ROOT / "experiments" / "openrouter_game_study"
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS = {
    "gpt_5_6_sol": "openai/gpt-5.6-sol",
    "claude_opus_5": "anthropic/claude-opus-5",
    "llama_3_3_70b": "meta-llama/llama-3.3-70b-instruct",
    "qwen_3_8_27b": "qwen/qwen3.8-27b",
    "deepseek_v4_flash": "deepseek/deepseek-v4-flash-0731",
}

REQUIRED_METHODS = {
    "players": ["self"],
    "initial_state": ["self"],
    "legal_actions": ["self", "state", "player"],
    "transition": ["self", "state", "joint_action"],
    "observation": ["self", "state", "joint_action", "next_state", "player"],
    "reward": ["self", "state", "joint_action", "next_state", "player"],
    "is_terminal": ["self", "state"],
}

SYSTEM_PROMPT = """You generate a finite executable POSG world model.
Return ONLY Python source defining exactly `class GeneratedPOSG(AbstractPOSG)`.
Do not use Markdown fences, imports, file/network access, eval, exec, or redefine AbstractPOSG.

The implementation MUST satisfy this exact interface:
class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["player_1", "player_2"]
    def initial_state(self): return "s0"
    def legal_actions(self, state, player): return ["action"]
    def transition(self, state, joint_action): return {"terminal": 1.0}
    def observation(self, state, joint_action, next_state, player): return "observation"
    def reward(self, state, joint_action, next_state, player): return 0.0
    def is_terminal(self, state): return state == "terminal"

Hard contract (checked exhaustively):
- Every player ID, state ID, action ID, and observation MUST be a string on EVERY branch.
- Use one uniform state representation: strings only. Never return tuple/list/dict state IDs.
- players is a non-empty list[str] with unique IDs.
- initial_state() returns one non-terminal string state (not a distribution).
- legal_actions() returns a non-empty list[str] for every player in every reachable non-terminal state.
- joint_action is a dict keyed by the exact IDs in players. Read it only by those string keys.
- transition() returns a non-empty dict[str, float] for every reachable joint action; probabilities
  are finite, non-negative, at most 1, and sum to exactly 1.0.
- observation() returns str for every player/outcome. Encode multiple fields as one f-string;
  NEVER return a tuple, list, dict, or set.
- reward() returns a finite int/float (not bool); is_terminal() returns bool.
- All seven methods and the players @property must be present with exactly the signatures above.
- Keep the reachable model finite and small (prefer <= 100 states and <= 10 decision steps).
- Implement the supplied game's strategic choices, chance, information, rewards, and terminal outcomes.
Before answering, silently verify every return path against this contract.
"""

USER_TEMPLATE = """Create a situation-specific GeneratedPOSG for this game case.

GAME CASE:
{description}
"""

REPAIR_TEMPLATE = """Your previous implementation failed mechanical validation.
Return a COMPLETE replacement class, not a patch and not an explanation.
Do not repeat the previous implementation unchanged. Trace the exact reachable
state/next_state branch named by each error. Every method must return on every
reachable control-flow path: add an unconditional final string fallback to
observation(), a finite numeric fallback such as 0.0 to reward(), a non-empty
list[str] fallback to legal_actions() for non-terminal states, and a valid
dict[str, float] fallback to transition() wherever a conditional chain could
otherwise fall through and implicitly return None.

VALIDATION ERRORS:
{errors}

PREVIOUS CODE:
{code}
"""


def load_dotenv(path: Path = REPO_ROOT / ".env") -> None:
    if not path.is_file():
        return
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip("\"'"))


def load_cases() -> dict[str, dict[str, str]]:
    cases: dict[str, dict[str, str]] = {}
    paths = sorted(CASE_ROOT.glob("game_G_*_Game_Situation_G*.md"), key=lambda p: int(re.search(r"G_(\d+)", p.name).group(1)))
    for path in paths:
        text = path.read_text(encoding="utf-8")
        number = int(re.search(r"G_(\d+)", path.name).group(1))
        match = re.search(r"(?:^|\n)#{0,3}\s*LLM Input\s*\n+(.*?)(?=\n\s*#{0,3}\s*Expected LLM Output|\Z)", text, re.DOTALL | re.IGNORECASE)
        if not match:
            raise ValueError(f"Could not extract LLM Input from {path}")
        cases[f"G{number}"] = {"description": match.group(1).strip(), "source": str(path.relative_to(REPO_ROOT))}
    if len(cases) != 9:
        raise ValueError(f"Expected G1-G9, found {sorted(cases)}")
    return cases


def extract_python(reply: str) -> tuple[str, str | None]:
    """Extract a class even when a model forgot or failed to close its fence."""
    text = (reply or "").strip()
    if not text:
        return "", "empty response"
    text = re.sub(r"^.*?</think>\s*", "", text, flags=re.DOTALL | re.IGNORECASE)
    fence = re.search(r"```(?:python)?\s*([\s\S]*?)(?:```|\Z)", text, re.IGNORECASE)
    if fence:
        text = fence.group(1).strip()
    class_start = re.search(r"(?m)^class\s+GeneratedPOSG\s*\(", text)
    if class_start:
        text = text[class_start.start():]
        text = re.sub(r"\n```[\s\S]*$", "", text).rstrip()
    try:
        ast.parse(text)
    except SyntaxError as error:
        return text, f"SyntaxError: {error}"
    return text, None


def static_contract_errors(source: str) -> list[str]:
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        return [f"SyntaxError: {error}"]
    errors: list[str] = []
    forbidden = (ast.Import, ast.ImportFrom, ast.With, ast.AsyncWith)
    for node in ast.walk(tree):
        if isinstance(node, forbidden):
            errors.append(f"line {node.lineno}: imports/context-manager I/O are forbidden")
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in {"eval", "exec", "open", "compile", "__import__", "input"}:
            errors.append(f"line {node.lineno}: call to {node.func.id}() is forbidden")
    classes = [node for node in tree.body if isinstance(node, ast.ClassDef) and node.name == "GeneratedPOSG"]
    if len(classes) != 1:
        errors.append(f"Expected exactly one GeneratedPOSG class; found {len(classes)}")
        return errors
    cls = classes[0]
    if not any(isinstance(base, ast.Name) and base.id == "AbstractPOSG" for base in cls.bases):
        errors.append(f"line {cls.lineno}: GeneratedPOSG must inherit AbstractPOSG")
    methods = {node.name: node for node in cls.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    for name, expected in REQUIRED_METHODS.items():
        method = methods.get(name)
        if method is None:
            errors.append(f"GeneratedPOSG is missing {name}()")
            continue
        actual = [arg.arg for arg in method.args.args]
        if actual != expected or method.args.vararg or method.args.kwarg or method.args.kwonlyargs:
            errors.append(f"line {method.lineno}: {name} signature expected {expected}, got {actual}")
        if name == "observation":
            for node in ast.walk(method):
                if isinstance(node, ast.Return) and isinstance(node.value, (ast.Tuple, ast.List, ast.Dict, ast.Set)):
                    errors.append(f"line {node.lineno}: observation() returns {type(node.value).__name__}, must return str")
    players = methods.get("players")
    if players and not any(isinstance(dec, ast.Name) and dec.id == "property" for dec in players.decorator_list):
        errors.append(f"line {players.lineno}: players must be decorated with @property")
    return errors


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return repr(value)


def probe_source(source_path: Path, output_path: Path, max_states: int, max_depth: int) -> int:
    source = source_path.read_text(encoding="utf-8")
    report: dict[str, Any] = {"status": "failed", "stage": "static", "errors": static_contract_errors(source), "warnings": []}
    if not report["errors"]:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            execution = execute_generated_posg(source)
            if not execution["success"]:
                report.update(stage=execution["stage"], errors=execution["errors"])
            else:
                model = execution["world_model"]
                rollout = rollout_world_model(model, max_states=max_states, max_depth=max_depth)
                errors = list(rollout["errors"])
                non_strings = [repr(state) for state in rollout["states"] if not isinstance(state, str)]
                if non_strings:
                    errors.append("Every reachable state ID must be str; non-string states: " + ", ".join(non_strings[:10]))
                if rollout["truncated"]:
                    errors.append("Reachability exploration was truncated; keep the model finite and within limits")
                report.update(
                    stage="rollout",
                    errors=errors,
                    warnings=rollout["warnings"],
                    states_checked=len(rollout["states"]),
                    transitions_checked=len(rollout["transitions"]),
                )
                if not errors:
                    try:
                        summary = WorldModelEDA.from_rollout(rollout).summary()
                        graph = build_state_graph(rollout)
                        report.update(
                            status="passed",
                            stage="complete",
                            eda_summary=_json_safe(summary),
                            graph={"nodes": [str(node) for node in graph.nodes], "edges": [[str(a), str(b)] for a, b in graph.edges]},
                            world_model=json.loads(canonical_rollout_json(rollout)),
                        )
                    except Exception as error:
                        report.update(stage="eda", errors=[f"{type(error).__name__}: {error}"])
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if report["status"] == "passed" else 1


class OpenRouterClient:
    def __init__(self, api_key: str, timeout: float, retries: int, max_tokens: int) -> None:
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is missing from .env")
        self.api_key, self.timeout, self.retries, self.max_tokens = api_key, timeout, retries, max_tokens

    def generate(self, model: str, messages: list[dict[str, str]]) -> tuple[str, dict[str, Any]]:
        payload = {
            "model": model,
            "messages": messages,
            "temperature": 0,
            "max_tokens": self.max_tokens,
            # Code-only tasks do not benefit from spending the output budget on hidden reasoning.
            "reasoning": {"enabled": False},
        }
        last_error: Exception | None = None
        for attempt in range(1, self.retries + 1):
            started = time.perf_counter()
            try:
                response = requests.post(
                    OPENROUTER_URL,
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json", "HTTP-Referer": "https://github.com/world-model-suite", "X-Title": "World Model Game Study"},
                    json=payload,
                    timeout=self.timeout,
                )
                if response.status_code in {408, 409, 429} or response.status_code >= 500:
                    raise requests.HTTPError(f"retryable HTTP {response.status_code}: {response.text[:500]}", response=response)
                response.raise_for_status()
                body = response.json()
                choice = body["choices"][0]
                content = choice.get("message", {}).get("content") or ""
                meta = {
                    "request_id": body.get("id"),
                    "model_returned": body.get("model"),
                    "provider": body.get("provider"),
                    "finish_reason": choice.get("finish_reason"),
                    "usage": body.get("usage"),
                    "seconds": round(time.perf_counter() - started, 3),
                    "attempt": attempt,
                }
                if not content:
                    raise RuntimeError(f"empty content (finish_reason={meta['finish_reason']!r})")
                return content, meta
            except (requests.RequestException, ValueError, KeyError, IndexError, RuntimeError) as error:
                last_error = error
                if attempt == self.retries:
                    break
                time.sleep(min(2 ** (attempt - 1), 8))
        raise RuntimeError(f"OpenRouter request failed after {self.retries} attempts: {last_error}")


def run_probe(module_path: Path, report_path: Path, timeout: float, max_states: int, max_depth: int) -> dict[str, Any]:
    command = [sys.executable, str(Path(__file__).resolve()), "--probe", str(module_path), str(report_path), "--max-states", str(max_states), "--max-depth", str(max_depth)]
    try:
        proc = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        report = {"status": "failed", "stage": "timeout", "errors": [f"Probe exceeded {timeout}s"], "warnings": []}
        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
        return report
    if not report_path.exists():
        return {"status": "failed", "stage": "probe_crash", "errors": [(proc.stderr or proc.stdout)[-1500:]], "warnings": []}
    return json.loads(report_path.read_text(encoding="utf-8"))


def save_pth(report: Mapping[str, Any], destination: Path) -> str | None:
    if report.get("status") != "passed" or not report.get("graph"):
        return None
    try:
        import torch
    except ImportError:
        return None
    nodes = list(report["graph"]["nodes"])
    index = {node: i for i, node in enumerate(nodes)}
    edges = report["graph"]["edges"]
    edge_index = torch.tensor([[index[a] for a, _ in edges], [index[b] for _, b in edges]], dtype=torch.long) if edges else torch.empty((2, 0), dtype=torch.long)
    torch.save({"node_ids": nodes, "edge_index": edge_index, "world_model": report["world_model"]}, destination)
    return str(destination)


def write_overview(run_dir: Path, run_id: str) -> None:
    (run_dir / "00_START_HERE.md").write_text(
        f"""# Hardened OpenRouter game POSG run `{run_id}`

All inputs and outputs for this run are contained here. First-pass generations are
preserved separately from repaired attempts so benchmark reporting does not inflate
the unaided pass rate.

- `00_run_info/`: configuration, resumable records, and summary files
- `01_inputs/`: exact cases and prompts
- `02_model_outputs/`: untouched replies and extracted Python
- `03_validation/`: subprocess probe reports
- `04_world_models/`: canonical JSON and PyTorch graph artifacts for passing attempts

Mechanical PASS means executable and contract-valid, not semantically correct.
""",
        encoding="utf-8",
    )


def run_study(args: argparse.Namespace) -> tuple[Path, list[dict[str, Any]]]:
    load_dotenv()
    cases = load_cases()
    selected_cases = args.cases or list(cases)
    selected_models = args.models or list(MODELS)
    unknown_cases, unknown_models = set(selected_cases) - set(cases), set(selected_models) - set(MODELS)
    if unknown_cases or unknown_models:
        raise ValueError(f"Unknown cases={sorted(unknown_cases)}, models={sorted(unknown_models)}")
    run_id = args.run_id or ("game-posg-" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    run_dir = OUTPUT_ROOT / run_id
    if run_dir.exists() and not args.resume:
        raise FileExistsError(f"Run already exists; pass --resume to continue: {run_dir}")
    layout = {
        "info": run_dir / "00_run_info", "cases": run_dir / "01_inputs" / "game_cases",
        "prompts": run_dir / "01_inputs" / "prompts_sent", "raw": run_dir / "02_model_outputs" / "raw_replies",
        "code": run_dir / "02_model_outputs" / "generated_python", "probe": run_dir / "03_validation" / "probe_reports",
        "models": run_dir / "04_world_models",
    }
    for path in layout.values():
        path.mkdir(parents=True, exist_ok=True)
    write_overview(run_dir, run_id)
    for case in selected_cases:
        source = REPO_ROOT / cases[case]["source"]
        (layout["cases"] / source.name).write_text(source.read_text(encoding="utf-8"), encoding="utf-8")
    config = {
        "run_id": run_id, "created_utc": datetime.now(timezone.utc).isoformat(), "models": {key: MODELS[key] for key in selected_models},
        "cases": selected_cases, "samples_per_case": args.samples, "max_repair_rounds": args.max_repair_rounds,
        "max_tokens": args.max_tokens, "reasoning_enabled": False, "strict_string_identifiers": True,
    }
    (layout["info"] / "config.json").write_text(json.dumps(config, indent=2) + "\n", encoding="utf-8")
    records_path = layout["info"] / "records.jsonl"
    records = [json.loads(line) for line in records_path.read_text(encoding="utf-8").splitlines() if line.strip()] if records_path.exists() else []
    completed = {record["tag"] for record in records}
    client = OpenRouterClient(os.getenv("OPENROUTER_API_KEY", ""), args.timeout, args.retries, args.max_tokens)

    total = len(selected_models) * len(selected_cases) * args.samples
    cell_number = 0
    for model_slug in selected_models:
        for case_id in selected_cases:
            for sample in range(1, args.samples + 1):
                cell_number += 1
                latest_code = ""
                latest_errors = ""
                for repair_round in range(args.max_repair_rounds + 1):
                    tag = f"{model_slug}_{case_id}_s{sample:02d}_r{repair_round}"
                    if tag in completed:
                        prior = next(record for record in records if record["tag"] == tag)
                        if prior["status"] == "passed" or repair_round == args.max_repair_rounds:
                            break
                        latest_code = (layout["code"] / f"{tag}.py").read_text(encoding="utf-8") if (layout["code"] / f"{tag}.py").exists() else ""
                        latest_errors = "\n".join(prior.get("errors", []))
                        continue
                    user = USER_TEMPLATE.format(description=cases[case_id]["description"])
                    if repair_round:
                        user += "\n\n" + REPAIR_TEMPLATE.format(errors=latest_errors[:5000], code=latest_code[:30000])
                    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user}]
                    (layout["prompts"] / f"{tag}.txt").write_text("SYSTEM:\n" + SYSTEM_PROMPT + "\nUSER:\n" + user, encoding="utf-8")
                    started = time.perf_counter()
                    try:
                        raw, meta = client.generate(MODELS[model_slug], messages)
                        backend_error = None
                    except Exception as error:
                        raw, meta, backend_error = "", {}, f"{type(error).__name__}: {error}"
                    (layout["raw"] / f"{tag}.txt").write_text(raw, encoding="utf-8")
                    code, extraction_error = extract_python(raw)
                    latest_code = code
                    module_path = layout["code"] / f"{tag}.py"
                    report_path = layout["probe"] / f"{tag}.json"
                    if code:
                        module_path.write_text(code.rstrip() + "\n", encoding="utf-8")
                        report = run_probe(module_path, report_path, args.probe_timeout, args.max_states, args.max_depth)
                    else:
                        report = {"status": "failed", "stage": "generation", "errors": [backend_error or extraction_error or "no code extracted"], "warnings": []}
                        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
                    if extraction_error and code and report["status"] != "passed" and extraction_error not in report["errors"]:
                        report["errors"].insert(0, extraction_error)
                        report_path.write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
                    latest_errors = "\n".join(report["errors"])
                    saved: list[str] = []
                    if report["status"] == "passed":
                        model_dir = layout["models"] / tag
                        model_dir.mkdir(parents=True, exist_ok=True)
                        json_path = model_dir / "world_model.json"
                        json_path.write_text(json.dumps(report["world_model"], indent=2, sort_keys=True) + "\n", encoding="utf-8")
                        saved.append(str(json_path.relative_to(run_dir)))
                        pth = save_pth(report, model_dir / "world_model_graph.pth")
                        if pth:
                            saved.append(str(Path(pth).relative_to(run_dir)))
                    record = {
                        "tag": tag, "model": model_slug, "model_id": MODELS[model_slug], "case": case_id, "sample": sample,
                        "repair_round": repair_round, "stage": "first_pass" if repair_round == 0 else "repair", "status": report["status"],
                        "failed_stage": None if report["status"] == "passed" else report["stage"], "errors": report["errors"],
                        "warnings": report.get("warnings", []), "states_checked": report.get("states_checked"),
                        "transitions_checked": report.get("transitions_checked"), "provider_meta": meta,
                        "total_seconds": round(time.perf_counter() - started, 3), "saved_artifacts": saved,
                    }
                    records.append(record)
                    with records_path.open("a", encoding="utf-8") as handle:
                        handle.write(json.dumps(record) + "\n")
                    print(f"[{cell_number:02d}/{total}] {tag}: {record['status'].upper()}" + (f" - {latest_errors[:140]}" if latest_errors else ""), flush=True)
                    if report["status"] == "passed":
                        break

    first = [record for record in records if record["repair_round"] == 0]
    final_by_cell: dict[tuple[str, str, int], dict[str, Any]] = {}
    for record in records:
        final_by_cell[(record["model"], record["case"], record["sample"])] = record
    summary = {
        "run_id": run_id, "expected_cells": total, "first_pass_passed": sum(r["status"] == "passed" for r in first),
        "final_passed": sum(r["status"] == "passed" for r in final_by_cell.values()), "final_failed": sum(r["status"] != "passed" for r in final_by_cell.values()),
        "attempt_count": len(records), "records": list(final_by_cell.values()),
    }
    (layout["info"] / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    with (layout["info"] / "summary.csv").open("w", newline="", encoding="utf-8") as handle:
        fields = ["model", "model_id", "case", "sample", "repair_round", "status", "failed_stage", "states_checked", "transitions_checked", "total_seconds"]
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader(); writer.writerows(final_by_cell.values())
    return run_dir, records


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe", nargs=2, metavar=("SOURCE", "REPORT"), help=argparse.SUPPRESS)
    parser.add_argument("--models", nargs="*", choices=sorted(MODELS))
    parser.add_argument("--cases", nargs="*", choices=[f"G{i}" for i in range(1, 10)])
    parser.add_argument("--samples", type=int, default=int(os.getenv("OPENROUTER_SAMPLES_PER_CASE", "1")))
    parser.add_argument("--max-repair-rounds", type=int, default=3)
    parser.add_argument("--max-tokens", type=int, default=int(os.getenv("OPENROUTER_MAX_TOKENS", "16384")))
    parser.add_argument("--timeout", type=float, default=float(os.getenv("OPENROUTER_TIMEOUT_SECONDS", "600")))
    parser.add_argument("--retries", type=int, default=int(os.getenv("OPENROUTER_MAX_RETRIES", "5")))
    parser.add_argument("--probe-timeout", type=float, default=60)
    parser.add_argument("--max-states", type=int, default=400)
    parser.add_argument("--max-depth", type=int, default=12)
    parser.add_argument("--run-id")
    parser.add_argument("--resume", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if args.probe:
        return probe_source(Path(args.probe[0]), Path(args.probe[1]), args.max_states, args.max_depth)
    if args.samples < 1 or args.max_repair_rounds < 0:
        raise ValueError("samples must be >= 1 and max-repair-rounds must be >= 0")
    destination, records = run_study(args)
    final: dict[tuple[str, str, int], str] = {}
    for record in records:
        final[(record["model"], record["case"], record["sample"])] = record["status"]
    passed = sum(status == "passed" for status in final.values())
    print(f"Completed: {passed}/{len(final)} cells mechanically valid.\nAll artifacts: {destination}")
    return 0 if passed == len(final) else 2


if __name__ == "__main__":
    raise SystemExit(main())
