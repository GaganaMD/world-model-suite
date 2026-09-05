# Local AI-control process-supervision reproduction

This isolated toy experiment asks whether a delegated worker can retain local action capability after a controller returns. It models 30 sequential tasks using a deterministic local mock provider. **No hosted model or OpenRouter access is required.**

Requirements: Python 3.10+ and the standard library. No `.env`, package install, credential, network, email, or external service is used.

From the repository root:

```powershell
python -m unittest discover -s experiments/ai_control_process_supervision/tests -v
python experiments/ai_control_process_supervision/scripts/run_baseline.py --mode normal --execution-id my_normal_run
python experiments/ai_control_process_supervision/scripts/run_baseline.py --mode fail-open --execution-id my_fail_open_run
python experiments/ai_control_process_supervision/scripts/run_baseline.py --mode in-flight --execution-id my_inflight_run
python experiments/ai_control_process_supervision/scripts/run_controlled_shutdown.py --execution-id my_controlled_run
```

Results are under `results/<execution-id>/`: immutable `config.json`, controller/worker/provider JSONL ledgers, `summary.json`, and `summary.md`. Execution IDs must be new; launchers refuse overwrite.

Safety properties: all provider actions are local ledger writes; no network library is used; the intentional fail-open child has a short independent watchdog deadline; controlled mode grants authority per task and stops at an explicit revocation boundary. See [REPORT.md](REPORT.md) for interpretation and limits.
