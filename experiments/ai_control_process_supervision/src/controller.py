"""Controller modes: normal, deliberately fail-open, in-flight stop, and fail-closed."""
from __future__ import annotations
import argparse, json, time
from pathlib import Path
from event_log import emit, read_events
from process_utils import count_events, launch_worker, terminate, wait_for_event

def write_stop(run_dir: Path, execution_id: str, ledger: Path, label: str) -> None:
    (run_dir / "stop.json").write_text(json.dumps({"execution_id": execution_id, "reason": label}), encoding="utf-8")
    emit(ledger, execution_id, "STOP_SIGNAL", reason=label)

def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--run-dir", type=Path, required=True); ap.add_argument("--execution-id", required=True); ap.add_argument("--mode", choices=["normal", "fail-open", "in-flight", "controlled"], required=True)
    args = ap.parse_args(); run_dir = args.run_dir; cfg = json.loads((run_dir / "config.json").read_text()); ledger = run_dir / "controller_events.jsonl"
    emit(ledger, args.execution_id, "CONTROLLER_START", mode=args.mode); child = launch_worker(run_dir, args.execution_id, cfg)
    wait_for_event(run_dir / "worker_events.jsonl", "WORKER_START", 2)
    if args.mode == "normal":
        child.wait(timeout=cfg["max_runtime_seconds"]); emit(ledger, args.execution_id, "RUN_COMPLETE", state="completed"); return
    if args.mode == "fail-open":
        time.sleep(cfg["controller_wait_seconds"]); alive = child.poll() is None
        emit(ledger, args.execution_id, "CHILD_ALIVE_CHECK", alive=alive); emit(ledger, args.execution_id, "CONTROLLER_TIMEOUT")
        emit(ledger, args.execution_id, "CONTROLLER_RETURN", child_pid=child.pid)
        # Intentionally no join or kill: worker's own deadline is the independent safety watchdog.
        return
    if args.mode == "in-flight":
        # Wait until the provider records an active request, then terminate before its response/metadata.
        wait_for_event(run_dir / "provider_events.jsonl", "PROVIDER_RECEIVED", cfg["controller_wait_seconds"] + 2)
        time.sleep(cfg["inflight_kill_delay_seconds"]); write_stop(run_dir, args.execution_id, ledger, "in_flight_termination")
        terminate(child); emit(ledger, args.execution_id, "WORKER_TERMINATED", terminated=True); emit(ledger, args.execution_id, "RUN_COMPLETE", state="terminated"); return
    # Fail-closed: grant explicit authority one task at a time, then revoke before task 10.
    for n in range(1, cfg["controlled_authorized_actions"] + 1):
        task_id = f"task_{n:03d}"
        deadline = time.monotonic() + 2
        while time.monotonic() < deadline:
            ready = [e for e in read_events(run_dir / "worker_events.jsonl") if e["event_type"] == "READY_FOR_AUTHORITY" and e["task_id"] == task_id]
            if ready: break
            time.sleep(.005)
        else: raise RuntimeError("worker did not request authority")
        (run_dir / "permit.json").write_text(json.dumps({"task_id": task_id}), encoding="utf-8")
        deadline = time.monotonic() + 2
        while count_events(run_dir / "worker_events.jsonl", "LOCAL_METADATA_WRITTEN") < n and time.monotonic() < deadline: time.sleep(.005)
    # Worker is waiting for authority for the next task, so revocation is an explicit fail-closed boundary.
    wait_for_event(run_dir / "worker_events.jsonl", "READY_FOR_AUTHORITY", 2)
    write_stop(run_dir, args.execution_id, ledger, "authority_revoked")
    child.wait(timeout=2); emit(ledger, args.execution_id, "REVOCATION_ACKNOWLEDGED")
    emit(ledger, args.execution_id, "RUN_COMPLETE", state="revoked")

if __name__ == "__main__": main()
