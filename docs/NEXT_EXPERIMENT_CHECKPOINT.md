# Next experiment checkpoint

## A. Trace-equivalence audit

- Behaviorally equivalent at H=3: 3 (Claude G1 runs 1--3).
- Behaviorally different: 0 established by the conservative comparator.
- Still ambiguous: 3 (Qwen G8 runs 1--2; Llama G9 run 1).

## B. Physical reference subset

P1--P5 are implemented in `experiments/build_physical_reference_subset.py`.
They contain 3/5/4/3/3 states respectively, canonical action vocabularies of
3/4/3/2/2, and 3/4/3/3/2 transition supports. Objectives and invariants are
external and machine-readable; reference generation is validated without LLM
calls.

## C. Controlled perturbations

Premature terminality gives regret 1.0; a spurious reverse edge changes
reversible edges 0 to 2; removing an action changes reachable states 3 to 2;
adding an action has no immediate regret for the calibration objective.

## D. Evaluation readiness

Structural F1: yes. Planning regret/policy agreement: yes for P1--P5 once a
generated artifact uses the canonical actions and external predicates.
Reachability/reversibility/unsafe-state metrics: yes. Existing G1--G9
generated candidates remain strict-ineligible.

## E. Generation readiness

Prompts and anti-leakage audit are ready. Planned first batch: 3 existing model
families × 5 environments × 2 generations = 30 calls; none launched.

## F--G. Claims

Current evidence supports structural disagreement and that controlled structural
errors can affect decision/reversibility metrics. It does not yet support a
generated-model planning-regret claim, long-horizon degradation claim, or real
physical safety claim.

## H. Highest-value next action

Authorize and run the 30-call Physical-AI batch only after reviewing the prompts
and reference summaries.
