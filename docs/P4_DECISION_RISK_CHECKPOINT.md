# P4 decision-risk checkpoint

The original P4 success-only objective has safe_route value 1 and risky_route
value `1-p`; safe_route therefore dominates for every positive risk and has
threshold `p*=0`. This is a benchmark/objective property, not an evaluator
failure, and the original calibration is preserved unchanged.

## P4b_COLLISION_RISK_TRADEOFF

The frozen external utility is success reward 1, safe-route cost 0.4, risky-route
cost 0.1, and collision penalty 0.35. Thus `U_safe=0.6` and
`U_risky(p)=0.9-1.35p`, giving the analytical threshold
`p*=0.3/1.35=2/9≈0.2222`. The reference risk is fixed at 0.5, so the reference
optimal action is safe_route with value 0.6.

Calibration probabilities are 0, .1, .2, .22, 2/9, .3, .5, and 1.0. Risky is
selected below the threshold; safe is selected above it; the threshold row is
reported with the planner's deterministic tie-breaking. In the policy-flip
case (assumed p=.1 while reference p=.5), transferred value is 0.325 and regret
is 0.275; reference collision probability is .5.

The P4 feature schema is unchanged and generated rewards remain excluded.
No hosted calls were made. The next exact three-call pilot is ready only after
using this frozen P4b scenario; the remaining clean 5×3×2 study requires 30
calls total (or 27 after a three-call pilot is accepted as its first run).
