"""Append-only, local JSONL event ledgers."""
from __future__ import annotations
import json, os, time
from datetime import datetime, timezone
from pathlib import Path

def emit(path: Path, execution_id: str, event_type: str, task_id: str | None = None, **extra: object) -> dict:
    event = {"timestamp": datetime.now(timezone.utc).isoformat(), "monotonic_timestamp": time.monotonic(),
             "pid": os.getpid(), "ppid": os.getppid(), "execution_id": execution_id,
             "task_id": task_id, "event_type": event_type, **extra}
    path.parent.mkdir(parents=True, exist_ok=True)
    # A single line append is sufficient for this one-writer-per-ledger toy experiment.
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(event, sort_keys=True) + "\n")
        f.flush()
    return event

def read_events(path: Path) -> list[dict]:
    if not path.exists(): return []
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]
