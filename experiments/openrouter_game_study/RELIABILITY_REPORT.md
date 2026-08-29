# Three-Run Game POSG Reliability

First-pass rate measures unaided generation reliability. Final rate includes explicitly
recorded mechanical repair rounds and measures whether the pipeline eventually produced
a usable contract-valid artifact. Neither metric is a semantic-quality score.

## By Run

| Run | First-pass valid | Final valid | Attempts | JSON | PTH |
| :--- | ---: | ---: | ---: | ---: | ---: |
| run_1 | 43/45 (95.56%) | 45/45 (100.00%) | 47 | 45 | 45 |
| run_2 | 41/45 (91.11%) | 45/45 (100.00%) | 50 | 45 | 45 |
| run_3 | 40/45 (88.89%) | 45/45 (100.00%) | 68 | 45 | 45 |

## Aggregate

- First-pass: 124/135 (91.85%)
- Repair-assisted final: 135/135 (100.00%)
- Stored artifacts: 135 JSON and 135 PTH

## First-Pass Reliability by Model

| Model | Passed/trials | Rate |
| :--- | ---: | ---: |
| claude_opus_5 | 27/27 | 100.00% |
| deepseek_v4_flash | 23/27 | 85.19% |
| gpt_5_6_sol | 26/27 | 96.30% |
| llama_3_3_70b | 22/27 | 81.48% |
| qwen_3_8_27b | 26/27 | 96.30% |

See `reliability_by_model_game.csv` for the 3-trial result of every model/game pair.
