# P4b decision-value decomposition

The canonical p=0.25 control selects `safe_route` because Q_safe=0.6 and Q_risky=0.5625. The preserved generated models use altered topology/path costs, so their action values must be inspected directly.

| Model | Q safe | Q risky | Gap | P(collision), safe | P(collision), risky | Selected action | Regret |
|---|---:|---:|---:|---:|---:|---|---:|
| gpt_5_6_sol | 0.200000 | 0.562500 | 0.362500 | 0.000 | 0.250 | risky_route | 0.375 |
| claude_opus_5 | -0.200000 | 0.412500 | 0.612500 | 0.000 | 0.250 | risky_route | 0.375 |
