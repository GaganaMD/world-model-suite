"""Run the per-task-authority, fail-closed controller."""
from __future__ import annotations
import argparse, json, subprocess, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]; SRC = ROOT / "src"; RESULTS = ROOT / "results"
def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--execution-id", required=True); ap.add_argument("--results-root", type=Path, default=RESULTS); args = ap.parse_args(); run_dir = args.results_root / args.execution_id
    if run_dir.exists(): raise SystemExit(f"refusing to overwrite existing run: {run_dir}")
    run_dir.mkdir(parents=True); cfg = json.loads((ROOT / "configs" / "baseline.json").read_text())
    cfg["watchdog_deadline"] = time.monotonic() + cfg["watchdog_seconds"]; cfg["require_per_task_permit"] = True
    (run_dir / "config.json").write_text(json.dumps(cfg, indent=2, sort_keys=True))
    subprocess.run([sys.executable, str(SRC / "controller.py"), "--run-dir", str(run_dir), "--execution-id", args.execution_id, "--mode", "controlled"], check=True)
    subprocess.run([sys.executable, str(Path(__file__).with_name("summarize_run.py")), "--run-dir", str(run_dir)], check=True)
    print(run_dir)
if __name__ == "__main__": main()
