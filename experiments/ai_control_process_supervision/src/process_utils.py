"""Small process and ledger helpers; no external services are used."""
from __future__ import annotations
import json, os, signal, subprocess, sys, time
from pathlib import Path
from event_log import read_events

def launch_worker(run_dir: Path, execution_id: str, config: dict) -> subprocess.Popen:
    cmd = [sys.executable, str(Path(__file__).with_name("sequential_worker.py")), "--run-dir", str(run_dir), "--execution-id", execution_id]
    # Separate process group models the surviving-child/orphan risk without shelling out.
    flags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
    return subprocess.Popen(cmd, creationflags=flags, env={**os.environ, "PYTHONPATH": str(Path(__file__).parent), "AI_CONTROL_CONFIG": json.dumps(config)})

def wait_for_event(path: Path, event_type: str, timeout: float) -> dict | None:
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        found = [e for e in read_events(path) if e["event_type"] == event_type]
        if found: return found[-1]
        time.sleep(.01)
    return None

def count_events(path: Path, event_type: str) -> int:
    return sum(e["event_type"] == event_type for e in read_events(path))

def terminate(process: subprocess.Popen, timeout: float = 2.0) -> bool:
    if process.poll() is None:
        process.terminate()
        try: process.wait(timeout=timeout)
        except subprocess.TimeoutExpired: process.kill(); process.wait(timeout=timeout)
    return process.poll() is not None
