# Matcher and planning decision

## Matcher conclusion

The improved score is a finite-horizon structural agreement measure with
permutation search over states/players. It does not measure semantic correctness,
observations, or payoff fidelity, and it can penalize state splitting/merging.
Its lower mean than the fallback is expected because the fallback only matched
global feature counts. The sanity suite passes, and the stratified audit found
objective topology discrepancies in 6/15 cases, ambiguity in 6/15, and no proven
matcher artifact.

## Planning eligibility

Reference objectives exist for G1--G9, but strict generated candidate
eligibility is currently 0 because action/reward alignment is not verified.

## Controlled perturbations

Premature terminality produced planning regret 1.0; a spurious reverse edge
changed reversible-edge count 0 to 2; removing an action reduced reachable
states 3 to 2 without changing this objective's optimum; adding an action had
no immediate regret. These are calibration results, not LLM evidence.

## Claim status

- Mechanical validity does not imply structural agreement: **SUPPORTED**.
- Mechanical validity does not imply structural fidelity: **PARTIAL** (structural, not semantic, and representation-sensitive).
- Structural fidelity predicts planning utility: **NOT TESTED**.
- Generated models alter policy choices: **NOT TESTED**.
- Generated models contain reachability/reversibility errors: **NOT TESTED**; controlled perturbations demonstrate the metric consequence only.

## Recommended titles

1. *Beyond Executability: Structural Agreement in LLM-Generated Executable POSGs*
2. *Mechanical Validity Does Not Imply Structural Agreement in LLM-Generated POSGs*
3. Current title, with an explicit representation-sensitive limitation.
