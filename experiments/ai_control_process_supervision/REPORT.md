# Process supervision as a local AI-control toy reproduction

## 1. Executive summary

This self-contained, local experiment reproduces an operational process-supervision failure: a controller returns while a sequential worker remains alive and continues to use a mock capability. In the measured fail-open run, the controller accounted for 8 actions, the worker survived controller return, and the provider received 5 more actions before a separate safety watchdog stopped the worker. A fail-closed, per-task authority mechanism produced zero provider requests after its revocation signal and acknowledgement.

This is an exploratory operational-control example. `control_gap` is novel local terminology in this report, not an established AI-control metric. Nothing here demonstrates deceptive, adversarial, or agentic intent.

## 2. Motivation and original incident

The motivating incident involved a planned 30-cell sequential collection. An external execution controller returned after 9 provider responses had been persisted, while a child collection process remained alive. Manual termination may have interrupted an in-flight request, leaving the exact number of requests beyond the 9 local records unprovable. No scientific output was evaluated. The factual, output-free account is in [docs/ORIGINAL_INCIDENT_SUMMARY.md](docs/ORIGINAL_INCIDENT_SUMMARY.md).

The original incident was an accidental orchestration failure, not evidence of deceptive or adversarial AI behavior.

## 3. Why this is AI-control relevant

Delegation often separates an overseer from a controller, worker, and side-effecting capability. Control can fail when revoking the controller's apparent execution does not revoke the worker's process lifetime or capability. This involves supervisory control, orphaned work, fail-open shutdown, capability revocation, and provenance/accountability. It is operational containment/control rather than adversarial AI-control research.

## 4. Threat model

The actors are a Human/Overseer, Controller, Worker/Agent, and External capability/provider. In a real system, assets could include network/API access, credentials, and authority to cause external effects. The failure condition is: the controller believes execution has stopped while delegated capability remains active. This reproduction replaces that capability with a local mock provider. Full detail: [docs/THREAT_MODEL.md](docs/THREAT_MODEL.md).

## 5. Architecture and event model

```text
Human/overseer
      |
      v
Controller ---- controller_events.jsonl
      |
      v
Sequential worker ---- worker_events.jsonl ---- local metadata files
      |
      v
Local mock provider ---- provider_events.jsonl
```

The worker schedules `task_001` through `task_030`, in order. Each action logs `REQUEST_START`, causes the provider to log `PROVIDER_RECEIVED`, waits 60 ms, logs `PROVIDER_RESPONSE`, and then writes local metadata plus `LOCAL_METADATA_WRITTEN`. Every ledger event includes UTC timestamp, monotonic timestamp, PID, PPID, execution ID, task ID, and event type. The ledgers are append-only JSONL and intentionally separate controller-side, worker-side, and provider-side evidence.

The only consulted reference was `final_study_v2/run_confirmatory_collection.py`, used solely to understand its sequential single-transport-call loop. No frozen prompt, scientific artifact, generated output, evaluator, or confirmatory runtime code is copied or imported. See [docs/EXPERIMENT_DESIGN.md](docs/EXPERIMENT_DESIGN.md).

## 6. Baseline and in-flight reproduction

The fail-open controller intentionally performs no join or termination after its timeout/return. A worker-side deadline is an independent hard safety watchdog to prevent an indefinite orphan. It is deliberately not credited as a containment control.

The in-flight variant waits until provider receipt, waits 15 ms of the 60-ms simulated latency, then terminates the worker. The observed run recorded one provider receipt but no completed local metadata record. Thus local persistence cannot establish that exactly zero (or exactly one) provider actions happened without provider-side evidence.

## 7. Fail-closed intervention

The controlled run uses supervisor-issued, one-task permits. After task 9, the worker waits for authority for task 10. The controller writes a stop signal instead of a permit; the worker records it, terminates, and the controller records `REVOCATION_ACKNOWLEDGED`. This establishes a clean local revocation boundary for this design. It does not claim to solve arbitrary races, descendants, kernel failures, or remote-provider cancellation.

## 8. Metrics

`planned_actions` is 30. `controller_accounted_actions` counts local metadata persisted by controller return (or all local records when there is no early return). `provider_received_actions` and `persisted_responses` are independent counts. `post_controller_requests` and `post_stop_requests` count provider receipts after their respective controller ledger boundaries. `alive_descendants_after_controller_return` is the controller's child alive check. Duplicate and unmatched counts compare task IDs across ledgers.

`control_gap = provider_received_actions - controller_accounted_actions` is an exploratory local metric. `revocation_latency = timestamp(last consequential provider action) - timestamp(controller stop/return)`; a negative value means the final provider action preceded stop, while `null` means no applicable stop/return boundary. Provider/local discrepancy is represented by unmatched records.

## 9. Observed results

| Run | Returned early? | Worker survived? | Provider | Persisted | Post-controller | Post-stop | Control gap | Revocation latency (s) | State |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| A normal | no | no | 30 | 30 | 0 | 0 | 0 | n/a | completed |
| B fail-open | yes | yes | 13 | 13 | 5 | 0 | 5 | n/a | controller returned |
| C in-flight | no | no | 1 | 0 | 0 | 0 | 1 | -0.047 | terminated |
| D controlled | no | no | 9 | 9 | 0 | 0 | 0 | -0.110 | revoked |

Run locations are `results/run_a_normal_v1`, `results/run_b_fail_open_v2`, `results/run_c_inflight_v1`, and `results/run_d_controlled_v1`. An earlier immutable fail-open calibration run is also retained as `run_b_fail_open_v1`; it is not used in the table.

## 10. Interpretation and relationship to AI control

The fail-open result demonstrates a process-lifecycle gap: controller return did not revoke a surviving worker's local capability. The in-flight result demonstrates a provenance gap: provider receipt and local persistence are different events. The controlled result demonstrates only that this local per-task authorization protocol had zero post-stop provider receipts after acknowledgement.

This toy testbed may later support adversarial-agent experiments, but none have been performed. In particular, it does not test a model intentionally preserving capability. It concerns operational containment, not model alignment claims.

## 11. Future work

Future work could test intentionally delegated descendants, delayed jobs, scheduled tasks, nested subprocesses, cloud job submission, capability leases, scoped short-lived credentials, heartbeat authority, provider-side cancellation, and adversarial attempts to preserve capability after revocation. A lease-based capability control was not implemented here to keep the initial reproduction small and directly auditable.

## 12. Limitations

This is a same-host Python toy with a mock provider, deterministic timing, one worker, and cooperative file-based signaling. PID liveness is only a point-in-time observation. The provider ledger is local rather than independently durable. The termination mismatch is timing-dependent, though this run observed it. The fail-closed invariant applies after the design's acknowledgement boundary, not to every possible operating-system or remote-service failure.

## 13. Reproduction instructions

Use the commands in [README.md](README.md). Each takes a new execution ID. The targeted test suite has bounded subprocess timeouts and cleans its temporary child processes. No external network access or `.env` is needed.

## 14. File map

- `src/event_log.py`: event schema and JSONL append/read helpers.
- `src/mock_provider.py`: deterministic local provider.
- `src/sequential_worker.py`: thirty-task worker and watchdog/permit behavior.
- `src/controller.py`: all four controller modes.
- `src/process_utils.py`: worker launch, liveness, and bounded termination.
- `scripts/`: immutable-run launchers and metric summarizer.
- `configs/baseline.json`: common deterministic timing/count configuration.
- `tests/`: local unit and process-supervision tests.
- `results/`: preserved ledgers, configuration, and summaries for observed runs.
