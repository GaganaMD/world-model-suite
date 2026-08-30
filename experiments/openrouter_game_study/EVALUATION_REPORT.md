# Three-Run Evaluation Results

## Aggregate

- Evaluated world models: **135**
- Lane 1 mechanical passes: **134/135**
- Lane 3 checklist passes: **135/135**
- Overall passes under available references: **134/135**
- Evaluation graph artifacts: **270 `.pth` files**

## Lane 2 Scope

Reference POSG documents now exist for **all G1-G9** cases, so Lane 2 scored
**135** candidates and skipped **0**.
The external `game_matching` package is unavailable in this workspace; scored rows
therefore use the pipeline's documented feature-multiset fallback. Their mean
combined score is **0.7162** and must not be presented as an optimal
graph-matching score.

## Lane 1 Failures

- `run_1/deepseek_v4_flash_G9_s01_r0`: see its `evaluation_report.json` for Lane 1 errors.

Detailed reports and candidate/ground-truth graph artifacts are stored under each
run's `05_evaluation/<model_game_attempt>/` directory.
