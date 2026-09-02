# P4b pilot manual audit

| Candidate | Classification | Verified evidence |
|---|---|---|
| GPT-5.6 Sol | planning-eligible with decision-relevant risk/dynamics error | Lane-1 and feature checks pass; initial canonical action is `risky_route`; generated risky branch has collision mass 0.25; transferred reference value is 0.225 versus safe optimum 0.6. |
| Claude Opus 5 | planning-eligible with decision-relevant risk/dynamics error | Same objective discrepancy; generated topology and costs yield `risky_route`, with immediate collision mass 0.25. |
| Llama 3.3 70B | mechanical failure | Rollout exposes empty transition distributions; no planning or structural metrics are defined. |

No artifact was modified during inspection. The GPT/Claude policy flip is
not attributed to risk probability alone: their generated topology/cost
structure also differs from the frozen direct-route calibration.
