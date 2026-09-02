# Generated-policy → reference-world regret checkpoint

A. Planning regret is implemented for explicit feature-based objectives using
finite-horizon dynamic programming; generated-candidate transfer is ready but
has no eligible candidate yet.

B. External objectives are independent of generated rewards.

C. Policy mapping is deterministic by canonical feature equality and rejects
missing or ambiguous mappings.

D. P1–P5 reference planners are validated with optimal value 1.0 and actions:
open_door, pick_up, move, safe_route, press_switch.

E. Controlled perturbations produce sensible consequences: premature terminality
regret 1.0; reverse edge changes reversibility 0→2; action removal changes
reachability 3→2 without regret; added action has no immediate regret.

F. P4 calibration preserves the null result: safe_route is selected for all
tested collision probabilities, with threshold p*=0 and regret 0.

G. Existing generated candidates eligible: **NO**.

H. New three-call state-feature pilot: ready, not launched.

I. Hosted calls in this task: **NO**.

J. Remaining 24 calls: remain paused.
