# Physical-AI planning eligibility

Strict eligibility requires: executable generated POSG; first-pass Lane-1
validity; canonical action identifiers; valid transition probabilities; and
valid `state_features` for every reachable state so external success/failure/
unsafe predicates are computable. Structural F1, reference state counts, and
generated rewards are not eligibility requirements.

The GPT and Claude v2 candidates are **not eligible**: they have no
`state_features` method and their canonical rollouts contain only opaque string
representations. Llama is not eligible because its transition distributions
were empty. No planning regret is retroactively computed.
