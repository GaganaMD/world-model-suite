"""Thirty-action sequential worker for the local process-supervision experiment."""
from __future__ import annotations
import argparse, json, os, time
from pathlib import Path
from event_log import emit
from mock_provider import invoke

def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--run-dir", type=Path, required=True); ap.add_argument("--execution-id", required=True)
    args = ap.parse_args(); cfg = json.loads(os.environ["AI_CONTROL_CONFIG"]); run_dir = args.run_dir
    worker_ledger = run_dir / "worker_events.jsonl"; stop_file = run_dir / "stop.json"; permit_file = run_dir / "permit.json"
    emit(worker_ledger, args.execution_id, "WORKER_START")
    try:
        for n in range(1, cfg["planned_actions"] + 1):
            task_id = f"task_{n:03d}"
            # The independent deadline is the hard watchdog: it bounds a fail-open child.
            if time.monotonic() >= cfg["watchdog_deadline"]:
                emit(worker_ledger, args.execution_id, "WATCHDOG_STOP", task_id); break
            if cfg.get("require_per_task_permit"):
                emit(worker_ledger, args.execution_id, "READY_FOR_AUTHORITY", task_id)
                while not permit_file.exists() and not stop_file.exists() and time.monotonic() < cfg["watchdog_deadline"]:
                    time.sleep(.005)
                if stop_file.exists(): emit(worker_ledger, args.execution_id, "STOP_SIGNAL", task_id); break
                permit = json.loads(permit_file.read_text(encoding="utf-8"))
                if permit.get("task_id") != task_id: raise RuntimeError("stale or incorrect authority permit")
                permit_file.unlink()
            if stop_file.exists(): emit(worker_ledger, args.execution_id, "STOP_SIGNAL", task_id); break
            emit(worker_ledger, args.execution_id, "REQUEST_START", task_id)
            response = invoke(run_dir, args.execution_id, task_id, cfg["latency_seconds"])
            meta = run_dir / "metadata" / f"{task_id}.json"; meta.parent.mkdir(exist_ok=True)
            meta.write_text(json.dumps(response, sort_keys=True), encoding="utf-8")
            emit(worker_ledger, args.execution_id, "LOCAL_METADATA_WRITTEN", task_id)
        else: emit(worker_ledger, args.execution_id, "WORKER_COMPLETED")
    finally:
        emit(worker_ledger, args.execution_id, "WORKER_TERMINATED")

if __name__ == "__main__": main()
