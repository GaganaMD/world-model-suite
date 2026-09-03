# Physical-AI final study protocol (frozen)

Version `physical-ai-v1`; no hosted calls have been made under this protocol.

### Protocol-completeness repair after failed preflight

The original intended-design freeze was commit `45b4fc2`. Before any clean
sample existed, preflight found missing P1/P2/P3/P5 reference files, missing
per-scenario prompt hashes, and a P4/P4b naming inconsistency. Zero final calls
were made. This repair materializes the committed intended definitions and
exact rendered prompts without changing task semantics; the repair commit is
the executable pre-data freeze.

## Design

The clean study contains five reference-backed symbolic embodied POSGs (P1
Blocked-Door Navigation, P2 Fragile Object Delivery, P3 Battery-Constrained
Delivery, P4 Collision-Risk Navigation, and P5 Irreversible Switch), three
models (`openai/gpt-5.6-sol`, `anthropic/claude-opus-5`,
`meta-llama/llama-3.3-70b-instruct`), and two independent generations per
model/scenario: 5 × 3 × 2 = **30 fresh calls**. Earlier P4/P4b pilots are
development evidence and are excluded from final aggregates.

## Frozen inputs

Each scenario uses its checked-in reference implementation, canonical action
vocabulary, and the final shared Python `GeneratedPOSG(AbstractPOSG)` scaffold.
Every reachable state must expose the scenario's canonical `state_features`
schema (documented in `docs/PHYSICAL_AI_STATE_FEATURE_CONTRACT.md`). External
success, failure, unsafe, and resource predicates are authoritative;
generated `reward()` is diagnostic only. Exact prompts are stored per scenario
with SHA-256 hashes in `experiments/physical_ai_subset/final_study/prompts/`.

P4b uses the frozen tradeoff objective (success 1.0, safe cost .4, risky cost
.1, collision penalty .35, reference risk .5), `p*=2/9`, and safe-route
reference optimum. It records `p_gen` jointly with `Q_safe`, `Q_risky`, and
`Q_gap`; p_gen alone is never treated as an explanation of policy choice.

## Evaluation and eligibility

The immutable order is provider status → static contract → feature contract →
Lane 1 → bounded rollout → permutation-aware structural comparison → strict
planning eligibility → generated-policy planning → canonical feature/initial
decision transfer → reference execution → regret and safety metrics.
Eligibility requires executable, Lane-1-valid, normalized transitions, valid
features on all reachable states, computable external predicates, canonical
actions, and deterministic policy transfer. Structural F1, equal state counts,
and generated rewards are not eligibility requirements. Failed stages leave
downstream fields `NA`; no retries, repairs, manual corrections, or
post-observation regeneration are permitted.

## Recorded metrics and aggregation

For every candidate record provider/contract/Lane-1 status, feature validity,
structural F1/exact match, policy/action agreement and mapping coverage,
generated/reference values and regret, success/failure/unsafe probabilities,
and environment-specific reachability/reversibility. P4b additionally records
the risk and Q-value fields above. Results are reported as counts, individual
values, and descriptive means/medians; two runs per cell do not support strong
reliability claims or unregistered significance testing. Error attribution is
descriptive (interface, feature, probability, terminality, topology/path-cost,
action-set, compound dynamics, decision-correct despite disagreement, or
unresolved) and is never inferred from F1 alone.

## Reproducibility and accounting

`experiments/physical_ai_subset/final_study/protocol.json` is the machine
readable identity/configuration. Candidate IDs are scenario/model/run plus the
prompt hash. The final-results schema is fixed before generation. Pilot/debug
artifacts remain under their original directories and are not overwritten.
