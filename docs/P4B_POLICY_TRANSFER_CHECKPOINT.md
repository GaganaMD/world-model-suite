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
