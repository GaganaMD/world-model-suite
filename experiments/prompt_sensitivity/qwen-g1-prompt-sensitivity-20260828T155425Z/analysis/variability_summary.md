# Repeated-generation robustness summary

Descriptive statistics only; this report makes no statistical-significance claim.

| Model | Case | Prompt | Attempts | Structural success | Same signature among structurally valid rollouts | Failures |
| --- | --- | --- | ---: | ---: | ---: | --- |
| qwen | G1 | P0 | 5 | 0.00 | N/A | {"invalid_actions": 5} |
| qwen | G1 | P1 | 5 | 0.20 | 1.00 | {"reward_failure": 4} |
| qwen | G1 | P2 | 5 | 1.00 | 1.00 | {} |

## G1 sample comparison

| Sample | Prompt | Status | States | Terminals | Edges | Max depth | Branching | Entropy | Δ states | Δ terminals | Δ edges |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | P0 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 2 | P0 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 3 | P0 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 4 | P0 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 5 | P0 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 1 | P1 | success | 4 | 3 | 4 | 1 | 2.25 | 0.9208605994871285 | 0 | 0 | 1 |
| 2 | P1 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 3 | P1 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 4 | P1 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 5 | P1 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 1 | P2 | success | 4 | 3 | 4 | 1 | 2.25 | 0.8146187299249081 | 0 | 0 | 1 |
| 2 | P2 | success | 4 | 3 | 4 | 1 | 2.25 | 1.0 | 0 | 0 | 1 |
| 3 | P2 | success | 4 | 3 | 4 | 1 | 2.25 | 1.0 | 0 | 0 | 1 |
| 4 | P2 | success | 4 | 3 | 4 | 1 | 2.25 | 1.0 | 0 | 0 | 1 |
| 5 | P2 | success | 4 | 3 | 4 | 1 | 2.25 | 1.0 | 0 | 0 | 1 |
