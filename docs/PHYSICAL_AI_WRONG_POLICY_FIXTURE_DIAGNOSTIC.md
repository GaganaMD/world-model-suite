# Wrong-policy fixture diagnostic

The frozen transfer implementation for this evaluator is initial-decision
transfer. Reference initial action spaces are:

| Scenario | Initial actions | Later decisions | Strategy |
|---|---|---|---|
| P1 | `open_door`, `move_right` | one continuation (`move_right`) | initial alternative |
| P2 | `pick_up` | `deliver` / `drop` | initial action effectively forced |
| P3 | `move`, `charge` | `deliver` | initial alternative (`charge` is a self-loop) |
| P4b | `safe_route`, `risky_route` | none | initial alternative |
| P5 | `press_switch` | `move` | initial action effectively forced |

The finite-horizon reference values are 1.0 for P1/P2/P3/P5 and 0.6 for
P4b. P2 and P5 have no distinct initial action that is both a meaningful
transfer target and a suboptimal decision under the frozen interface; their
later decisions are single-action continuations. Constructing positive-regret
later-policy fixtures for these scenarios would require extending the frozen
initial-only transfer semantics, so they are not manufactured here.

P4b remains the designated positive-regret wrong-initial-action control.
