# Experiment design

The design abstracts a sequential 30-cell collection loop without importing it or any scientific inputs. `controller.py` starts `sequential_worker.py`, which calls `mock_provider.py` once per task. The provider is a local function which records receipt, sleeps for deterministic latency, and records a response.

Four modes share `configs/baseline.json`: normal completion; fail-open controller return without a join; termination shortly after provider receipt; and a fail-closed controller that grants one explicit permit per task and revokes before task 10. The fail-open worker has a deadline supplied at launch. That independent watchdog is a test-environment bound, not the control intervention.

Each run is immutable: launch scripts refuse an existing execution ID. Three append-only JSONL ledgers record controller, worker, and provider observations with UTC and monotonic timestamps, PID, PPID, execution ID, task ID, and event type.

Consulted implementation reference: `experiments/physical_ai_subset/final_study_v2/run_confirmatory_collection.py`, solely to identify the sequential, one-transport-call-per-cell orchestration pattern. This experiment does not import it at runtime and does not use prompts, candidate matrices, outputs, evaluator code, or credentials.
