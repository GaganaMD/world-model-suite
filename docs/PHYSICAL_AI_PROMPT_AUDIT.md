# Physical-AI prompt audit

The redesigned prompt supplies interface information (the preloaded base class,
exact class/method signatures, argument names, return contracts, and a minimal
fill-in skeleton) plus the scenario, canonical action vocabulary, probability
rules, terminal representation, and machine-readable state fields. Interface
information is not world-model answer leakage. The prompt does not reveal the
reference transition graph, state/edge counts, optimal policy, or evaluation
scores. Exact action identifiers guarantee action alignment by construction;
external objective predicates remain separate from generated reward values.
The revised state-semantic addendum additionally requires a `state_features`
method with the case-specific canonical fields documented in
`PHYSICAL_AI_STATE_FEATURE_CONTRACT.md`; this exposes ontology, not dynamics.
