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
The original `evaluation_summary.csv` preserves the pipeline's feature-multiset
fallback (mean **0.7162**) for historical traceability. The paper-strengthening
analysis restores the intended pinned `game_matching` backend and writes its
permutation-invariant results separately under `paper_results/` and
`paper_structural_comparison.csv`. Its mean is **0.3639** over all 135 final
artifacts and **0.3660** among the 134 Lane-1 passes. Do not mix the two backends.

## Lane 1 Failures

- `run_1/deepseek_v4_flash_G9_s01_r0`: see its `evaluation_report.json` for Lane 1 errors.

Detailed reports and candidate/ground-truth graph artifacts are stored under each
run's `05_evaluation/<model_game_attempt>/` directory.
