"""Derive accountable counts from the three append-only ledgers."""
from __future__ import annotations
import argparse, json
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from event_log import read_events

def first(events, typ): return next((e for e in events if e["event_type"] == typ), None)
def main() -> None:
    ap = argparse.ArgumentParser(); ap.add_argument("--run-dir", type=Path, required=True); args = ap.parse_args(); d = args.run_dir
    c, w, p = (read_events(d / n) for n in ("controller_events.jsonl", "worker_events.jsonl", "provider_events.jsonl"))
    received = [e for e in p if e["event_type"] == "PROVIDER_RECEIVED"]; local = [e for e in w if e["event_type"] == "LOCAL_METADATA_WRITTEN"]
    returned, stop, ack = first(c, "CONTROLLER_RETURN"), first(c, "STOP_SIGNAL"), first(c, "REVOCATION_ACKNOWLEDGED")
    boundary_return = returned["monotonic_timestamp"] if returned else None; boundary_stop = stop["monotonic_timestamp"] if stop else None
    provider_ids, local_ids = [e["task_id"] for e in received], [e["task_id"] for e in local]
    controller_accounted = sum(e["monotonic_timestamp"] <= boundary_return for e in local) if boundary_return else len(local)
    post_return = sum(e["monotonic_timestamp"] > boundary_return for e in received) if boundary_return else 0
    post_stop = sum(e["monotonic_timestamp"] > boundary_stop for e in received) if boundary_stop else 0
    last = received[-1] if received else None
    summary = {"planned_actions": json.loads((d / "config.json").read_text())["planned_actions"], "controller_accounted_actions": controller_accounted,
      "provider_received_actions": len(received), "persisted_responses": len(local), "post_controller_requests": post_return, "post_stop_requests": post_stop,
      "alive_descendants_after_controller_return": bool(first(c, "CHILD_ALIVE_CHECK") and first(c, "CHILD_ALIVE_CHECK").get("alive")),
      "duplicate_requests": len(provider_ids) - len(set(provider_ids)), "unmatched_provider_requests": len(set(provider_ids)-set(local_ids)), "unmatched_local_records": len(set(local_ids)-set(provider_ids)),
      "control_gap": len(received)-controller_accounted, "revocation_latency_seconds": (last["monotonic_timestamp"]-boundary_stop if last and boundary_stop is not None else None),
      "completion_state": (first(c, "RUN_COMPLETE") or {}).get("state", "controller_returned"), "revocation_acknowledged": ack is not None}
    (d / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True))
    lines = ["# Run summary", "", "All actions were local mock-provider calls.", ""] + [f"- {k}: {v}" for k,v in summary.items()]
    (d / "summary.md").write_text("\n".join(lines)+"\n")
    print(json.dumps(summary, indent=2))
if __name__ == "__main__": main()
