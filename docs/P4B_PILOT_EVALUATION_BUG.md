# P4b pilot evaluation bug

The three authorized P4b calls completed, but evaluation must not be treated as
valid pilot evidence. The runner still loaded the legacy `P4_collision_risk`
reference and tagged rows with that scenario, rather than loading the frozen
`P4b_COLLISION_RISK_TRADEOFF` reference and external objective. Consequently the
reported structural F1 values (GPT .2452; Claude .0812) are against the wrong
reference and are invalid for P4b.

The feature checker also encoded a restrictive P4 location domain
(`route/goal/collision`) even though the frozen ontology specifies `location`
as a string and generated candidates legitimately used labels such as
`destination` and `safe_corridor`. This is a checker-contract defect, not a
model failure.

The corrected offline evaluator now uses immutable P4b identity fields
(`scenario_id=P4b_COLLISION_RISK_TRADEOFF`, `reference_variant=p4b_v1`,
`objective_id=p4b_tradeoff_v1`) and rejects legacy references. Recomputed
structural F1 is GPT `0.2403`, Claude `0.1360`; Llama remains rollout-invalid.
Policy transfer is not complete, so no regret is claimed.

Affected fields: scenario labels, structural scores, and all downstream
eligibility/planning fields. Raw responses, parsed code, and original metadata
are preserved under `experiments/physical_ai_subset/p4b_pilot/`; no generated
file was changed and no calls were retried. No P4b pilot success decision is
made. The evaluator/reference configuration must be corrected and validated
offline before any new hosted calls.
