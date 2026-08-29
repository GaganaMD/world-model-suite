# Repeated-generation robustness summary

Descriptive statistics only; this report makes no statistical-significance claim.

| Model | Case | Prompt | Attempts | Structural success | Same signature among structurally valid rollouts | Failures |
| --- | --- | --- | ---: | ---: | ---: | --- |
| qwen_p0 | G1 | P0 | 5 | 0.00 | N/A | {"invalid_transition": 5} |
| qwen_p0 | G2 | P0 | 5 | 0.00 | N/A | {"invalid_actions": 5} |
| qwen_p0 | G3 | P0 | 5 | 0.00 | N/A | {"invalid_transition": 5} |
| qwen_p0 | G4 | P0 | 5 | 0.00 | N/A | {"invalid_actions": 5} |
| qwen_p0 | G5 | P0 | 5 | 0.00 | N/A | {"invalid_terminal_structure": 5} |
| qwen_p0 | G6 | P0 | 5 | 0.20 | N/A | {"execution_error": 1, "invalid_actions": 4} |
| qwen_p0 | G7 | P0 | 5 | 0.00 | N/A | {"invalid_transition": 5} |
| qwen_p0 | G8 | P0 | 5 | 0.00 | N/A | {"invalid_terminal_structure": 5} |
| qwen_p0 | G9 | P0 | 5 | 0.00 | N/A | {"invalid_actions": 5} |
| qwen_p1 | G1 | P1 | 5 | 0.00 | N/A | {"invalid_transition": 5} |
| qwen_p1 | G9 | P1 | 5 | 0.00 | N/A | {"invalid_actions": 5} |
| qwen_p2 | G1 | P2 | 5 | 0.00 | N/A | {"invalid_actions": 5} |
| qwen_p2 | G9 | P2 | 5 | 0.00 | N/A | {"invalid_actions": 5} |

## G1 sample comparison

| Sample | Prompt | Status | States | Terminals | Edges | Max depth | Branching | Entropy | Δ states | Δ terminals | Δ edges |
| ---: | --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| 1 | P0 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 2 | P0 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 3 | P0 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 4 | P0 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 5 | P0 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 1 | P1 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 2 | P1 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 3 | P1 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 4 | P1 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 5 | P1 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 1 | P2 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 2 | P2 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 3 | P2 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 4 | P2 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
| 5 | P2 | failed | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A | N/A |
