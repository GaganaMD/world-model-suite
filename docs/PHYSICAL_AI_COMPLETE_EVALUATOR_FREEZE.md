# Complete all-scenario evaluator freeze

This post-`db12299` integration freeze supplies the missing P1–P5 orchestration
using the existing planner, external predicates, feature contracts, and
reference specifications. `evaluate_candidate.py` provides scenario adapters;
`evaluate_final_study.py` runs reference self-tests and batch plumbing. The
component hashes are recorded in
`experiments/physical_ai_subset/final_study/evaluator_manifest.json`.

Reference self-tests pass for P1 (`open_door`, 1.0), P2 (`pick_up`, 1.0), P3
(`move`, 1.0), P4b (`safe_route`, 0.6), and P5 (`press_switch`, 1.0). Generated
rewards remain excluded from external objectives. No real collected outputs
were used and no hosted calls were made during this integration.

The synthetic 30-cell dry run produced 30 inputs and 30 unique outputs with
zero failures; all reference-equivalent candidates were planning eligible with
zero regret. The v2 preflight passed. The complete evaluator is frozen for
replacement data collection.
