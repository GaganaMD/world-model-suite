# Next experiments master

## Research questions

The extension tests whether structural errors affect decisions, reachability, reversibility, persistence, and long-horizon consequences.

## P0 -- planning utility

**Status: infrastructure ready; preserved-generation evaluation pending objective/action alignment.** A finite-horizon exact planner and reference-policy evaluator are in `src/planning/finite_horizon.py`. No arbitrary rewards are inferred.

## Structural fidelity versus planning

**Status: not yet supported on generated G1--G9.** This requires a validated mapping of generated actions and terminal rewards, not only graph-state alignment.

## Controlled perturbations

**Status: completed no-call calibration.** `experiments/run_controlled_perturbation_study.py` removes/adds actions, changes terminality, and adds a reverse edge in a tiny POSG, reporting value, regret, reachability, and reversibility.

## Reachability/reversibility

**Status: infrastructure ready; calibration included.** See `src/evaluation/reachability_metrics.py`.

## Cross-run policy stability

**Status: not yet tested.** Existing three-run structural stability is available, but policy comparison needs validated action alignment.

## Complexity

**Status: completed from existing artifacts.** The existing paper-results build reports descriptive G1--G9 associations; stochastic-profile fraction had Spearman rho -0.677 with mean matched F1 (n=9).

## Physical subset and horizon stress

**Status: pipeline and generation plan pending.** No new LLM calls or manuscript claims are made.

## Intervention consistency

**Status: not yet run on generated models.** Objective invariant checks are a planned no-call extension.
