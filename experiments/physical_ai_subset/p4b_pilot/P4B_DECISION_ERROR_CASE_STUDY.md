# P4b decision-error case study

The frozen reference has `p_ref=0.5`, selects `safe_route`, and has value
`0.6`. Both preserved executable candidates instead select `risky_route`.

| Model | F1 | p_gen | Q_safe | Q_risky | Selected | Reference value | Regret |
|---|---:|---:|---:|---:|---|---:|---:|
| GPT-5.6 Sol | 0.2403 | 0.25 | 0.2000 | 0.5625 | risky_route | 0.225 | 0.375 |
| Claude Opus 5 | 0.1360 | 0.25 | -0.2000 | 0.4125 | risky_route | 0.225 | 0.375 |

The canonical direct-route control at `p=0.25` has values `0.6` and
`0.5625`, so the scalar risk estimate alone does not explain the generated
choice. In the generated topologies, `safe_route` incurs additional
multi-step cost, while `risky_route` reaches a terminal outcome immediately.
This is a compound topology/path-cost error, not evidence that risk alone
crossed the frozen threshold. Both transferred policies expose collision
probability `0.5` in the reference world.
