# Stratified matcher case audit

Fifteen cases were selected deterministically from `paper_results/per_trial.csv`
across F1 strata, models, games, and runs. Artifact-level inspection compared
reference and generated state/action/edge counts and the saved generated JSON.
Cases with a clearly objective topology or terminality discrepancy are marked
confirmed; cases requiring semantic interpretation are marked ambiguous. No
case was labeled a matcher artifact without direct evidence.

| Stratum | Model/game/run | F1 | Fallback F1 | Reference states | Candidate states | Classification |
|---|---|---:|---:|---:|---:|---|
| exact | Claude G7 r1 | 1.0000 | 1.0000 | 5 | 5 | no discrepancy observed |
| exact | DeepSeek G4 r1 | 1.0000 | 1.0000 | 3 | 3 | no discrepancy observed |
| exact | DeepSeek G4 r2 | 1.0000 | 1.0000 | 3 | 3 | no discrepancy observed |
| high | GPT G4 r1 | 0.9238 | 1.0000 | 3 | 3 | confirmed probability/role mismatch |
| high | GPT G4 r2 | 0.9238 | 1.0000 | 3 | 3 | confirmed probability/role mismatch |
| high | GPT G4 r3 | 0.9238 | 1.0000 | 3 | 3 | confirmed probability/role mismatch |
| low | Claude G1 r1 | 0.2207 | 0.7857 | 4 | 10 | ambiguous granularity plus extra structure |
| low | Claude G1 r2 | 0.2207 | 0.7857 | 4 | 10 | ambiguous granularity plus extra structure |
| low | Claude G1 r3 | 0.2207 | 0.7857 | 4 | 10 | ambiguous granularity plus extra structure |
| very low | Claude G2 r1 | 0.0288 | 0.1029 | 4 | 73 | confirmed substantial topology expansion |
| very low | Claude G2 r2 | 0.0283 | 0.0980 | 4 | 38 | confirmed substantial topology expansion |
| very low | Claude G2 r3 | 0.0283 | 0.0980 | 4 | 38 | confirmed substantial topology expansion |
| very low | Claude G6 r1 | 0.0383 | 0.1029 | 5 | 101 | confirmed invented bid levels and phases |
| very low | Qwen G8 r1 | 0.0283 | 0.1667 | 5 | 18 | ambiguous state factoring; topology differs |
| very low | Llama G9 r1 | 0.0283 | 0.1667 | 5 | 17 | ambiguous state factoring; topology differs |

Summary: 6 cases have objective, directly inspectable discrepancies; 6 are
ambiguous because alternative state factoring or granularity could require
semantic review; 3 exact cases show the matcher can recognize equivalent
renamings/orderings. No matcher artifact was established. This is evidence for
structural disagreement, not a claim that all low-F1 cases are semantic errors.
