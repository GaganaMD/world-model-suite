# G1 prompt-sensitivity comparison

This is a controlled descriptive study of five requests per prompt condition
using `qwen2.5-coder:latest` and seeds 42--46. It makes no statistical
significance, generalization, causal, or evaluator-reliability claim.

| Variant | Structural success | Semantic success | Transition semantic PASS | Reward semantic PASS | Observation semantic PASS | Dominant failure | Reachable states | Terminal states | State-graph edges | Mean branching | Mean entropy | Max depth |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| P0 | 0/5 | 0/5 | N/A | N/A | N/A | `invalid_actions` (5/5) | N/A | N/A | N/A | N/A | N/A | N/A |
| P1 | 1/5 | 0/5 | 0/1 | 0/1 | 0/1, 1 UNKNOWN | `reward_failure` (4/5) | 4 | 3 | 4 | 2.25 | 0.921 | 1 |
| P2 | 5/5 | 0/5 | 0/5 | 0/5 | 0/5, all UNKNOWN | semantic transition/reward failure | 4 | 3 | 4 | 2.25 | 0.963 | 1 |
| P2_PLUS | 5/5 | 0/5 | 5/5 | 0/5 | 0/5, all FAIL | semantic reward/observation failure | 4 | 3 | 3 | 2.25 | 0.000 | 1 |

## Transition-structure result

P2 successful models add a stochastic return to `s0` from every action
profile, producing four state-graph edges and nonzero transition entropy.
Every P2_PLUS model instead has each of the nine action profiles transition
with probability 1.0 directly to one of three terminal outcome states. It has
three state-graph edges and zero transition entropy.

Therefore P2_PLUS eliminated the unjustified return-to-`s0` loop. It did not
achieve semantic success: all five P2_PLUS sources assign rewards by outcome
label without making them player-specific, and their player-2 winner/loser
observations contradict the actual outcome in the G1 oracle.
