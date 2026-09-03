# restart_03 confirmatory evaluation

## Inclusion
* Included: 30 restart_03 records only.
* Excluded: restart_01, restart_02, legacy, pilot/debug, and quarantined sources (0 rows each).

## Overall funnel

|Authorized|Provider success|Parse/execution|Feature|Lane1|Structural|Planning|Decision-transfer|
|---:|---:|---:|---:|---:|---:|---:|---:|
|30|30|10|10|10|10|10|3|

## Structural fidelity
Ten rows were structurally evaluable: mean F1 0.19549, median 0.18415, range 0.1362–0.2813, exact matches 0.

## Decision and regret
Numeric frozen-transfer outcomes were available for 3 rows: 1 agreement, 2 disagreement, 2 positive-regret, and 1 zero-regret. Mean regret 0.250; median 0.375; maximum 0.375.

## Main-text case
P4b_COLLISION_RISK_TRADEOFF_GPT_R2 had F1 0.2403. Its generated risky-route collision probability was 0.25, while the frozen reference probability is 0.5. Under the frozen external objective and finite-horizon planner, the generated model assigned Q_safe = 0.2000 and Q_risky = 0.5625, selecting risky_route. The reference policy selects safe_route with value 0.6; transferring risky_route yields reference value 0.225, regret 0.375, and reference collision probability 0.5. This is a consequential action-value and policy discrepancy in the generated world. It should not be attributed to collision probability alone: the generated model also represents a distinct safe-route topology, and both differences coexist in the candidate.

## Interpretation
Mechanical validity was necessary but not sufficient for structural fidelity in this sample. Structural mismatch did not map one-to-one onto initial-decision behavior: one low-F1 P2 candidate preserved the transferred decision, while two P4b candidates selected the unsafe reference-suboptimal route. These are descriptive benchmark observations, not a general reliability estimate.
