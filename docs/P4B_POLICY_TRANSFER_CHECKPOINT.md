# P4b policy-transfer checkpoint

The transfer rule maps a unique generated initial nonterminal state exposing
`safe_route` and `risky_route` directly to the reference initial decision
context. It does not use state-name equality, structural matcher alignment, or
generated rewards.

GPT and Claude are planning eligible; both select `risky_route`, with
`p_gen=.25`, `p_ref=.5`, risk error `.25`, initial policy agreement `0`,
transferred reference value `.225`, and regret `.375`. Collision probability
under each transferred policy is `.5` (unsafe delta `.5`). Llama is ineligible
because its transitions are empty. Structural F1 is GPT `.2403` and Claude
`.1360`, showing low structural agreement with a decision-relevant policy
error in this pilot. These remain pilot/debug results because evaluation was
repaired after generation.

No hosted calls were made. The pipeline is ready to freeze, but the clean final
study still requires 30 fresh calls.

## Action-value decomposition

The canonical `p=0.25` control selects `safe_route` (`Q_safe=.6` versus
`Q_risky=.5625`). Direct evaluation of the preserved generated models gives
GPT `Q_safe=.20, Q_risky=.5625` and Claude `Q_safe=-.20, Q_risky=.4125`.
Both models make the risky choice because their generated topology/path costs
alter the route values; `p_gen=.25` alone is not sufficient to explain it.
The decomposition and probability-weighted traces are in
`experiments/physical_ai_subset/p4b_pilot/corrected_eval/`.
