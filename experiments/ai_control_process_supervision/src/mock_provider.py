"""A deliberately local, deterministic stand-in for a consequential provider."""
from __future__ import annotations
import time
from pathlib import Path
from event_log import emit

def invoke(run_dir: Path, execution_id: str, task_id: str, latency_seconds: float) -> dict:
    emit(run_dir / "provider_events.jsonl", execution_id, "PROVIDER_RECEIVED", task_id)
    time.sleep(latency_seconds)
    emit(run_dir / "provider_events.jsonl", execution_id, "PROVIDER_RESPONSE", task_id)
    return {"task_id": task_id, "response": "local-mock-response"}
