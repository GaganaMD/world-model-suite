# Generated-Policy → Reference-World Regret

## 1. Research Question

Can a policy optimized inside an LLM-generated world model transfer to the
canonical reference environment?

## 2. Motivation

Mechanical validity and structural similarity are necessary checks, but they do
not establish that a model induces useful decisions. Regret evaluates the
generated policy where the ground-truth dynamics are fixed.

## 3. Experimental Principle

For reference model `M_ref` and candidate `M_gen`, derive `pi_ref` and `pi_gen`
using the same finite-horizon planner. The primary quantity is
`V_ref(pi_gen)`, with `regret = V_ref* - V_ref(pi_gen)` and
`V_ref* = V_ref(pi_ref)`. Generated `reward()` is never the primary objective.

## 4. Reference Environments

P1 blocked door, P2 fragile delivery, P3 battery delivery, P4 collision risk,
and P5 irreversible switch are small symbolic POSGs with explicit external
success/failure/unsafe predicates. Canonical action vocabularies and reference
summaries are in `physical_reference/`.

## 5. Canonical State Features

State IDs may differ. Future generated models must expose the canonical fields
in `docs/PHYSICAL_AI_STATE_FEATURE_CONTRACT.md`; policy transfer groups states by
identical feature maps, not by names.

## 6. External Objectives

`src/evaluation/physical_features.py` defines predicates. Generated rewards are
stored only as diagnostics and cannot declare a collision safe or a goal
successful.

## 7. Planning Eligibility

Eligibility requires executable Lane-1-valid dynamics, canonical actions,
normalized probabilities, valid features for every reachable state, computable
external predicates, and an unambiguous feature-based policy mapping.

## 8. Reference Planner Validation

`reference_results.csv` reports optimal value 1.0 for all five references. The
initial optimal actions are respectively `open_door`, `pick_up`, `move`,
`safe_route`, and `press_switch`.

## 9. Generated-Model Planning

`src/planning/finite_horizon.py` performs exact finite-horizon enumeration. A
future eligible candidate is optimized using external terminal predicates and
then evaluated in `M_ref`.

## 10. Policy Transfer

Reference decision states are mapped to generated states through canonical
features. Missing states or multiple states implying different actions make the
candidate ineligible; no manual resolution is permitted.

## 11. Metrics

Regret is reference optimal value minus transferred-policy reference value.
Policy agreement reports matching actions divided by mapped decision states;
mapping coverage reports mapped reference states divided by all reference
decision states. Success and unsafe probabilities are evaluated in the
reference world.

## 12. Controlled Validation

Existing calibration confirms that premature terminality causes regret 1.0,
while a spurious reverse edge changes reversibility without immediate regret.
These variants demonstrate metric sensitivity rather than LLM performance.

## 13. P4 Collision-Risk Calibration

The externally defined objective is success probability. The safe route always
reaches success, so the analytical decision boundary is `p*=0`: for any positive
collision probability the safe route is optimal. The calibration CSV evaluates
fixed risk values 0, .2, .5, .8, and 1.0; all select `safe_route` with reference
value 1 and regret 0. This null result is retained and was not tuned to induce
regret.

## P4 Decision-Relevant Risk Variant

The original success-only P4 is preserved as a negative control. Before any new
model outputs, we froze `P4b_COLLISION_RISK_TRADEOFF` with safe-route cost 0.4,
risky-route cost 0.1, success utility 1, and collision penalty 0.35. Thus
`U_safe=0.6`, `U_risky(p)=0.9-1.35p`, and `p*=2/9≈0.2222`. The reference risk
is 0.5. Beliefs below the threshold select risky and beliefs above it select
safe; at the threshold deterministic profile ordering selects risky. At belief
0.1, transferred value is 0.225 and regret is 0.375. This is a pre-registered
calibration, not an LLM result.

## 14. Existing Generated Candidates

The earlier GPT and Claude P4 candidates (F1=.9538) remain ineligible because
they lack `state_features`; Llama remains ineligible because its transitions
were empty. Their regret is NA.

## 15. Current Results

No generated candidate currently has measurable regret. `results.csv` is
reserved for eligible candidates and uses NA for undefined quantities.

## 16. Interpretation

All four combinations of structural similarity and decision regret are
possible in principle; none is claimed as observed in the current generated
sample.

## 17. Next Hosted Pilot

The next pilot is exactly three P4 calls (one per existing model family) using
the state-feature contract. It has not been run.

## 18. Limitations

The environments are symbolic, discrete, and small; objectives are simplified;
future generation counts are small; feature ontology is supplied to generators;
and this is not evidence of deployed-robot safety.

## 19. Reproduction

Run `python experiments/physical_ai_subset/planning_regret/run_reference_planning.py`
for no-call reference results. Run the existing controlled perturbation script
for calibration. No command in this directory makes hosted API calls.

## 20. Files

`reference_results.csv`, `p4_risk_calibration.csv`, and the planner/feature
modules provide machine-readable inputs for later generated-candidate runs.
