# Clean Physical-AI Final Study

## Frozen Protocol
Commit 71b05f9; 30 authorized cells.

## Dataset
30 provider responses preserved; no retries or repairs.

## Validity Funnel
Provider 30/30; contract 30/30; feature contract 16/30; Lane-1 20/30; planning eligible 14/30.

## Structural Fidelity
Structural F1 is NA because a post-run evaluator defect omitted the frozen
matcher invocation. No values are imputed.

## Planning Eligibility
14 candidates pass the automated eligibility stages.

## Decision Fidelity
Downstream values remain NA. The collection runner did not execute the full
frozen planning/transfer evaluator; see `docs/PHYSICAL_AI_FINAL_STUDY_EVALUATOR_BUG.md`.

## P4b Collision-Risk Tradeoff
Six P4b rows are preserved in `results/p4b_results.csv`.

## Failure Analysis
All failures remain represented in `final_results.csv`.

## Limitations
Collection-stage validity is reported separately from downstream metric availability.

## Reproducibility
Raw responses, request configurations, and parsed outputs are under this directory.
