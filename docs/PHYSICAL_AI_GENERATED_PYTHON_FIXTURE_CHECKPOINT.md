# Generated-Python Fixture Validation

At commit 0eaf049, executable `GeneratedPOSG(AbstractPOSG)` fixtures were
added for all five frozen scenarios. The fixtures are evaluated through the
same loader, contract/feature checks, Lane 1, planning, transfer, and regret
entry points used by the final-study pipeline. The generated-Python 30-cell
dry run produces 30 input and 30 output rows with no orchestration failures.

Reference-equivalent fixtures select the frozen reference actions and yield
zero regret. The P4b wrong fixture remains executable and structurally
evaluable while changing its risky branch, providing a valid dynamics
perturbation. No benchmark definitions, objectives, or real generated
artifacts were changed. The quarantined first collection was not read and no
hosted calls were made.

Validation: `tests/test_generated_python_fixtures.py` passes; full suite is
110 passed (pytest cache permission warning only). Dry-run artifacts are in
`experiments/physical_ai_subset/final_study_v2/generated_python_dry_run/`.
