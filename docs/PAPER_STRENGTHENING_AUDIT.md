# Paper strengthening audit

## Structural matcher

- **Old method:** name-insensitive feature-multiset overlap from `src/evaluation/lane2_structural.py`; it compares aggregate counts without optimizing state correspondence.
- **New method:** the existing `json_generation/gm_convert.py` adapter plus the intended `game_matching` implementation, pinned as `third_party/game_matching` at revision `76ca30bdfc2c44cad5fa5db98c3bdaef7d3fa629`.
- **Definition:** both POSGs become depth-three acyclic games. Hungarian assignments initialize player/state/action correspondences and seeded local search refines them (3,000 iterations, seed 0). Intrinsic action-conditioned structure is used because conversion deliberately assigns equal terminal payoffs. Coverage normalizes by the reference self-score, precision by the candidate self-score, and F1 is their harmonic mean.
- **Assumptions:** behavior beyond depth three is excluded; cycles are unrolled; observations and rewards are not compared; alignment is approximate; alternative valid granularities can score below one.
- **Tests:** 12 matcher/structural tests pass. Added tests cover state ordering, state/action/player renaming, missing support, extra action profiles, terminality, and transition probabilities.
- **Change:** among 134 Lane-1 passes, mean F1 changes from 0.7178 (fallback) to 0.3660 (matched); exact scores change from 32 to 28.

## Updated central numbers

- First-pass game validity: **124/135 (91.85%)**.
- Repair-assisted contract-valid final artifacts: **135/135**.
- Post-hoc Lane-1 validity: **134/135 (99.26%)**.
- Matched F1 over all 135: mean **0.3639**, median **0.1778**, Q1 **0.1258**, Q3 **0.5898**.
- Conditional on Lane-1 pass (n=134): mean **0.3660**, SD **0.3675**, median **0.1778**, Q1 **0.1258**, Q3 **0.7396**, IQR **0.6138**, min **0.0283**, max **1.0000**.
- Exact matched scores among Lane-1 passes: **28/134**.
- Descriptive counts: **33/134** at least 0.90, **34/134** at least 0.75, **100/134** below 0.75. These are not validated quality thresholds.

| Model | First pass | Lane 1 | Coverage | Precision | Mean F1 | Median [Q1, Q3] | Exact |
|---|---:|---:|---:|---:|---:|---:|---:|
| Claude Opus 5 | 27/27 | 27/27 | 0.3133 | 0.1416 | 0.1709 | 0.1128 [0.0597, 0.2312] | 1/27 |
| DeepSeek V4 Flash | 23/27 | 26/27 | 0.3255 | 0.2679 | 0.2696 | 0.1769 [0.1171, 0.1941] | 4/27 |
| GPT-5.6 Sol | 26/27 | 27/27 | 0.5558 | 0.4879 | 0.4981 | 0.2500 [0.1333, 1.0000] | 8/27 |
| Llama 3.3 70B | 22/27 | 27/27 | 0.5312 | 0.4528 | 0.4719 | 0.2000 [0.1461, 1.0000] | 9/27 |
| Qwen 3.8 27B | 26/27 | 27/27 | 0.4324 | 0.4147 | 0.4087 | 0.1778 [0.1524, 0.9441] | 6/27 |

Wilson intervals and game-clustered bootstrap intervals are in `experiments/openrouter_game_study/paper_results/summary.csv`.

## Run-to-run stability

Across 45 model-game pairs with three preserved generations: mean within-pair F1 SD is **0.1679**, median within-pair range is **0.0591**, all three runs exactly match the reference for **4/45** pairs, and all three generations are mutually structurally equivalent for **15/45** pairs.

Per-model mean SD / median range: Claude 0.0715 / 0.0005; DeepSeek 0.1775 / 0.1053; GPT 0.0618 / 0; Llama 0.1684 / 0.1184; Qwen 0.3601 / 0.7865. Three observations per pair support descriptive variation only.

## Complexity analysis

| Reference metric | Spearman rho with mean F1 |
|---|---:|
| states | 0.053 |
| terminal states | 0.053 |
| action profiles | 0.202 |
| transition supports | 0.009 |
| average branching | 0.053 |
| stochastic-profile fraction | -0.677 |

The stochasticity association has descriptive two-sided p=0.045, but n=9 is too small for confirmatory or causal inference.

## Failure case study

- **Game/model/run:** G6, Claude Opus 5, run 1 (`claude_opus_5_G6_s01_r0`).
- **Lane 1 / matched F1:** pass / 0.0383.
- **Verified mismatch:** the candidate introduces bids `{0,1,2,3}` although the case specifies two levels and explicitly disallows invented bid amounts. It expands the five-state reference into 101 states through a type draw, four type-conditioned bid states, 16 tie states, and 80 terminals.
- **Evidence:** preserved case rubric, raw response, and canonical world model under `experiments/openrouter_game_study/run_1/`.

## Figures/tables changed

- Added matched-F1 ECDF, within-pair stability plot, and compressed main-study G6 graph comparison.
- Split mechanical and matched structural tables; added Wilson intervals, median/IQR, exact counts, stability, and complexity summaries.

## Claims revised

- Narrowed the title from world-model fidelity to **structural fidelity**.
- Replaced the fallback as the headline game result while retaining it for traceability.
- Replaced pooled SD with within-model-game variation.
- Added one inspected unsupported expansion and separated it from automatic structural flags.

## Claims intentionally NOT made

- Graph differences are not automatically semantic errors; 0.75/0.90 are not fidelity categories.
- Complexity associations are not causal or confirmatory; three runs do not establish population stability.
- Automated Lane 3 is not human validated.
- No downstream planning, control, robotics, or real-world-safety result is claimed.

## Remaining weaknesses

- Matching is approximate and depth-bounded; alternative valid state splitting/merging can reduce scores.
- The complexity analysis has only nine games.
- Observations and rewards are preserved but excluded from the structural score.
- Human semantic annotation and downstream policy evaluation remain incomplete.
