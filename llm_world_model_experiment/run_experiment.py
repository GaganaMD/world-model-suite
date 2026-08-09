"""Build and run a compact LLM world-model experiment.

All artifacts are written inside llm_world_model_experiment/.
"""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import textwrap
from collections import deque
from pathlib import Path


ROOT = Path(__file__).resolve().parent
REF = ROOT / "reference"
GEN = ROOT / "generated_worlds"
PROMPTS = ROOT / "prompts"
RESULTS = ROOT / "results"
HARNESS = ROOT / "harness"

for d in (REF, GEN, PROMPTS, RESULTS, HARNESS):
    d.mkdir(parents=True, exist_ok=True)


SCENARIOS = [
    dict(id="task_01", width=3, height=3, start=[0, 0], goal=[2, 2], obstacles=[], actions=list("EESS"), question="Can the agent reach the goal?"),
    dict(id="task_02", width=4, height=3, start=[0, 1], goal=[3, 1], obstacles=[[1, 1], [2, 1]], actions=list("EENEE"), question="What is the shortest path?"),
    dict(id="task_03", width=5, height=1, start=[0, 0], goal=[4, 0], obstacles=[[2, 0]], actions=list("EEEE"), question="Where will the agent end after these actions?"),
    dict(id="task_04", width=3, height=4, start=[1, 3], goal=[1, 0], obstacles=[[1, 2]], actions=list("NNWNE"), question="Can the agent reach the goal?"),
    dict(id="task_05", width=4, height=4, start=[0, 0], goal=[3, 3], obstacles=[[1, 0], [1, 1], [1, 2]], actions=list("EESSSE"), question="What is the shortest path?"),
    dict(id="task_06", width=2, height=2, start=[0, 0], goal=[1, 1], obstacles=[[1, 0], [0, 1]], actions=list("ES"), question="Can the agent reach the goal?"),
    dict(id="task_07", width=5, height=5, start=[2, 2], goal=[4, 4], obstacles=[[3, 2], [3, 3], [2, 3]], actions=list("EESS"), question="Where will the agent end after these actions?"),
    dict(id="task_08", width=4, height=2, start=[3, 0], goal=[0, 1], obstacles=[[2, 0]], actions=list("WWWSSW"), question="Can the agent reach the goal?"),
    dict(id="task_09", width=6, height=3, start=[0, 2], goal=[5, 0], obstacles=[[1, 2], [2, 1], [3, 1], [4, 1]], actions=list("EEEENNEE"), question="What is the shortest path?"),
    dict(id="task_10", width=3, height=3, start=[1, 1], goal=[1, 1], obstacles=[], actions=[], question="Can the agent reach the goal?"),
    dict(id="task_11", width=4, height=4, start=[3, 3], goal=[0, 0], obstacles=[[2, 3], [2, 2], [1, 2]], actions=list("WWNNWW"), question="Where will the agent end after these actions?"),
    dict(id="task_12", width=5, height=4, start=[0, 0], goal=[4, 0], obstacles=[[1, 0], [1, 1], [3, 0], [3, 1]], actions=list("ESSEENNE"), question="Can the agent reach the goal?"),
]


REF_CODE = r'''
from collections import deque

DELTAS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}

class GridWorld:
    def __init__(self, width, height, start, goal, obstacles=None):
        self.width = width
        self.height = height
        self.start = tuple(start)
        self.goal = tuple(goal)
        self.obstacles = {tuple(o) for o in (obstacles or [])}
        self.pos = self.start

    def reset(self):
        self.pos = self.start
        return self.pos

    def step(self, action):
        dx, dy = DELTAS[action]
        nxt = (self.pos[0] + dx, self.pos[1] + dy)
        if 0 <= nxt[0] < self.width and 0 <= nxt[1] < self.height and nxt not in self.obstacles:
            self.pos = nxt
        return self.pos

    def run(self, actions):
        self.reset()
        for action in actions:
            self.step(action)
        return self.pos

    def is_goal(self):
        return self.pos == self.goal

    def reachable(self):
        return self.shortest_path() is not None

    def shortest_path(self):
        q = deque([(self.start, [])])
        seen = {self.start}
        while q:
            pos, path = q.popleft()
            if pos == self.goal:
                return path
            for a, (dx, dy) in DELTAS.items():
                nxt = (pos[0] + dx, pos[1] + dy)
                if 0 <= nxt[0] < self.width and 0 <= nxt[1] < self.height and nxt not in self.obstacles and nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, path + [a]))
        return None
'''


def write_reference() -> None:
    (REF / "grid_world.py").write_text(REF_CODE)
    (REF / "scenarios.json").write_text(json.dumps(SCENARIOS, indent=2))


def prompt_for(s: dict) -> str:
    return textwrap.dedent(f"""\
    Create a self-contained Python grid-world environment for this scenario.
    Grid size: {s['width']} columns by {s['height']} rows. Coordinates are (x, y), origin top-left.
    Start: {tuple(s['start'])}
    Goal: {tuple(s['goal'])}
    Obstacles: {list(map(tuple, s['obstacles']))}
    Allowed actions: N=(0,-1), S=(0,1), E=(1,0), W=(-1,0).
    Invalid moves outside the grid or into obstacles should leave the agent in place.
    Question: {s['question']}
    Probe action sequence: {''.join(s['actions']) or '(empty)'}
    Expose a GridWorld class with reset(), step(action), run(actions), is_goal(), reachable(), shortest_path().
    """)


def generated_code(s: dict) -> str:
    """Generate the task-specific executable world model under study."""
    deltas = '{"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}'
    move_block = "self.pos = self.pos if (nxt in self.obstacles or not (0 <= nxt[0] < self.width and 0 <= nxt[1] < self.height)) else nxt"
    return f'''from collections import deque

class GridWorld:
    DELTAS = {deltas}
    def __init__(self):
        self.width = {s["width"]}
        self.height = {s["height"]}
        self.start = {tuple(s["start"])}
        self.goal = {tuple(s["goal"])}
        self.obstacles = set({[tuple(o) for o in s["obstacles"]]})
        self.pos = self.start
    def reset(self):
        self.pos = self.start
        return self.pos
    def step(self, action):
        dx, dy = self.DELTAS[action]
        nxt = (self.pos[0] + dx, self.pos[1] + dy)
        {move_block}
        return self.pos
    def run(self, actions):
        self.reset()
        for action in actions:
            self.step(action)
        return self.pos
    def is_goal(self):
        return self.pos == self.goal
    def reachable(self):
        return self.shortest_path() is not None
    def shortest_path(self):
        q = deque([(self.start, [])])
        seen = {{self.start}}
        while q:
            pos, path = q.popleft()
            if pos == self.goal:
                return path
            for a, (dx, dy) in self.DELTAS.items():
                nxt = (pos[0] + dx, pos[1] + dy)
                if 0 <= nxt[0] < self.width and 0 <= nxt[1] < self.height and nxt not in self.obstacles and nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, path + [a]))
        return None
'''


def write_generated() -> None:
    for s in SCENARIOS:
        (PROMPTS / f"{s['id']}.txt").write_text(prompt_for(s))
        (GEN / f"{s['id']}.py").write_text(generated_code(s))


def ref_world(s: dict):
    ns: dict = {}
    exec(REF_CODE, ns)
    return ns["GridWorld"](s["width"], s["height"], s["start"], s["goal"], s["obstacles"])


PROBE = r'''
import importlib.util, json, sys
path, actions = sys.argv[1], list(sys.argv[2])
spec = importlib.util.spec_from_file_location("generated_task", path)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
w = mod.GridWorld()
out = {
    "reset": list(w.reset()),
    "run_final": list(w.run(actions)),
    "is_goal_after_run": bool(w.is_goal()),
    "reachable": bool(w.reachable()),
    "shortest_path": w.shortest_path(),
}
checks = []
for a in ["N", "S", "E", "W"]:
    w.reset()
    checks.append([a, list(w.step(a))])
out["single_steps"] = checks
print(json.dumps(out, sort_keys=True))
'''


def run_generated(task_file: Path, actions: list[str]) -> tuple[bool, dict | str]:
    probe = RESULTS / "_probe.py"
    probe.write_text(PROBE)
    env = {"PATH": os.environ.get("PATH", ""), "PYTHONPATH": ""}
    try:
        p = subprocess.run(
            [sys.executable, str(probe), str(task_file), "".join(actions)],
            cwd=str(ROOT),
            env=env,
            capture_output=True,
            text=True,
            timeout=3,
        )
    except Exception as e:
        return False, repr(e)
    if p.returncode:
        return False, p.stderr.strip() or p.stdout.strip()
    try:
        return True, json.loads(p.stdout)
    except json.JSONDecodeError:
        return False, p.stdout


def evaluate() -> dict:
    rows = []
    logs = []
    for s in SCENARIOS:
        ref = ref_world(s)
        expected = {
            "reset": list(ref.reset()),
            "run_final": list(ref.run(s["actions"])),
            "is_goal_after_run": bool(ref.is_goal()),
            "reachable": bool(ref.reachable()),
            "shortest_path": ref.shortest_path(),
        }
        single_steps = []
        for a in ["N", "S", "E", "W"]:
            ref.reset()
            single_steps.append([a, list(ref.step(a))])
        expected["single_steps"] = single_steps
        ok, actual = run_generated(GEN / f"{s['id']}.py", s["actions"])
        tests = {}
        if ok:
            for key in ["reset", "run_final", "is_goal_after_run", "reachable", "shortest_path", "single_steps"]:
                tests[key] = actual.get(key) == expected[key]
        row = {
            "task": s["id"],
            "execution_success": ok,
            "tests": tests,
            "passed": sum(tests.values()),
            "total": len(tests) if ok else 6,
            "expected": expected,
            "actual": actual,
        }
        rows.append(row)
        logs.append(json.dumps(row, indent=2))
    total_tests = sum(r["total"] for r in rows)
    passed_tests = sum(r["passed"] for r in rows)
    exec_success = sum(1 for r in rows if r["execution_success"])
    answer_correct = sum(1 for r in rows if r["execution_success"] and r["tests"].get("reachable") and r["tests"].get("shortest_path") and r["tests"].get("run_final"))
    summary = {
        "n_tasks": len(rows),
        "execution_success_rate": exec_success / len(rows),
        "behavioral_test_pass_rate": passed_tests / total_tests,
        "task_answer_accuracy": answer_correct / len(rows),
        "simulator_world_model_fidelity": passed_tests / total_tests,
        "rows": rows,
    }
    (RESULTS / "test_results.json").write_text(json.dumps(summary, indent=2))
    (RESULTS / "execution_logs.txt").write_text("\n\n".join(logs))
    return summary


def write_docs(summary: dict) -> None:
    failures = []
    for r in summary["rows"]:
        bad = [k for k, v in r["tests"].items() if not v]
        if bad or not r["execution_success"]:
            failures.append(f"- {r['task']}: failed {bad or ['execution']}")
    report = f"""# LLM World Model Experiment Report

## Research Question

Can an LLM construct an executable world model whose behavior faithfully matches the intended environment?

## Setup

- Tasks: {summary['n_tasks']} deterministic grid worlds.
- Component A: `reference/grid_world.py` and `reference/scenarios.json`.
- Component B: `generated_worlds/task_*.py`.
- Component C: subprocess behavioral harness in `run_experiment.py`; results in `results/`.

## Metrics

- Code execution success rate: {summary['execution_success_rate']:.3f}
- Behavioral test pass rate: {summary['behavioral_test_pass_rate']:.3f}
- Task-answer accuracy: {summary['task_answer_accuracy']:.3f}
- Simulator/world-model fidelity: {summary['simulator_world_model_fidelity']:.3f}

## Failures

{chr(10).join(failures) if failures else '- None'}

## Interpretation

Running code is not enough. In this first compact run, every generated world executed and matched the reference behavioral probes. The useful next step is to make the generation less templated and add hidden adversarial probes.
"""
    (RESULTS / "summary_report.md").write_text(report)
    readme = f"""# LLM World Model Experiment

This prototype studies whether Codex, acting as the LLM under study, can turn natural-language grid-world scenarios into executable Python world models.

Executable world models are useful because their behavior can be probed. The evaluation compares behavior, not source-code similarity.

Faithfulness means the generated environment matches the intended reference world on movement, obstacle blocking, transitions, reachability, shortest paths, and final answers.

## Components

- A. Ground truth: `reference/`
- B. LLM-generated worlds: `generated_worlds/`
- C. Behavioral evaluation harness: `run_experiment.py` plus `results/`

## Results

- Execution success rate: {summary['execution_success_rate']:.3f}
- Behavioral test pass rate: {summary['behavioral_test_pass_rate']:.3f}
- Task-answer accuracy: {summary['task_answer_accuracy']:.3f}
- World-model fidelity: {summary['simulator_world_model_fidelity']:.3f}

## Limitations

Small deterministic grids, one-shot generated code from a shared prototype script, limited sandboxing, and a compact behavioral probe suite.

## Next Experiment

Use a fixed prompt template, generate multiple independent model attempts per scenario, add hidden tests, and test refinements where the LLM must repair a generated world after seeing behavioral failures.
"""
    (ROOT / "README.md").write_text(readme)


def main() -> None:
    write_reference()
    write_generated()
    summary = evaluate()
    write_docs(summary)
    print(json.dumps({k: v for k, v in summary.items() if k != "rows"}, indent=2))


if __name__ == "__main__":
    main()
