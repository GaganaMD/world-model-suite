# v3 JSON-Track Run — Zero-Shot v3 Prompt

## What this is

A complete JSON world-model generation run for the 12 cases `data/README.md`
classifies as **JSON / Both** on the JSON track: the ten toy cases **T1.1–T4.4** and
the first two game cases **G.1, G.2**.

- **Prompt:** `prompts_library/zero_shot_v3_prompt.md` — the v3 zero-shot schema
  prompt. It keeps the validated v2 wire format (`players` / `initial` / `states`
  with `turn`, `by`, `next`) and adds a **papers-grounded design provenance**
  (References: Salge & Polani 2017; Turner et al. 2020; Klyubin et al. 2005; Amodei
  et al. 2016; Ha & Schmidhuber 2018; Konidaris et al. 2018; Krakovna et al. 2020;
  Eysenbach et al. 2018; Du et al. 2020; Cao et al. 2025; Dainese et al. 2024;
  Estrada 2012; Dalrymple et al. 2024; Heitzig & Potham 2026; Zou et al. 2026).
- **Generator honesty note:** no LLM credentials are configured in this workspace
  (`OPENROUTER_API_KEY` / `GROQ_API_KEY` absent), so the 12 candidates were
  **authored offline, by hand, strictly following the v3 prompt**, one model per
  case derived from that case's `### LLM Input` situation. This is recorded in
  `_manifest.json`. When credentials are available, the same run can be reproduced
  with:

  ```powershell
  python json_generation/generate.py --cases-dir data/Test_Cases/01_toy --k 1
  python json_generation/generate.py --cases-dir data/Test_Cases/03_game --k 1
  ```

## Files

| Path | Contents |
|---|---|
| `_manifest.json` | run provenance: prompt path + sha256, generator, banks, case list |
| `<case>.json` (x12) | the generated world models (v2 schema) |
| `evaluation_summary.json` | full per-case metrics + aggregates |
| `evaluation_results/<case>/evaluation_report.json` | the three-lane pipeline's own report per case |
| `graphs/<case>/full_<case>.png` | fully annotated transition graph |
| `graphs/<case>/depth_<d>.png` | **step-by-step diagrams** — one image per BFS depth layer |
| `README.md` | this overview |

## Evaluation used

Each candidate is scored by the repository pipeline `src/evaluation` (Lane 1
mechanical, Lane 2 structural vs. the authored reference converted to v2, Lane 3
qualitative) plus **extended metrics** (in `evaluation_summary.json`):

- **Lane 1 + extended:** schema/G-rules verdict; also `n_states`, `n_terminal`,
  `n_joint_actions`, `avg_branching`, distribution **entropy (bits)**,
  `reachability_coverage`, `max/mean_terminal_depth`, `cyclic` / SCC count.
- **Lane 2 + extended:** coverage / precision / combined F1 (feature-multiset
  fallback — `game_matching` is not installed), plus a full per-feature
  `lane2_feature_diff` (matched / delta / missing / extra).
- **Lane 3 + extended:** checklist + bias scan; also `human_agents_present`,
  `humans_act_somewhere`, `action_counts_by_player`, `outcome_granularity`.

## Results (overview)

| Case | L1 | L3 | Overall | L2 cov | L2 prec | L2 comb | States | Depth layers |
|---|---|---|---|---|---|---|---|---|
| toy_1_1 | PASS | ok | PASS | 1.000 | 1.000 | 1.000 | 4 | 0–1 |
| toy_1_2 | PASS | ok | PASS | 1.000 | 1.000 | 1.000 | 5 | 0–1 |
| toy_2_1 | PASS | ok | PASS | 0.688 | 0.898 | 0.779 | 7 | 0–4 |
| toy_2_2 | PASS | ok | PASS | 0.531 | 0.944 | 0.680 | 8 | 0–2 |
| toy_3_1 | PASS | ok | PASS | 1.000 | 1.000 | 1.000 | 6 | 0–2 |
| toy_3_2 | PASS | ok | PASS | 0.654 | 0.878 | 0.750 | 5 | 0–3 |
| toy_4_1 | PASS | ok | PASS | 1.000 | 1.000 | 1.000 | 4 | 0–1 |
| toy_4_2 | PASS | ok | PASS | 1.000 | 1.000 | 1.000 | 5 | 0–1 |
| toy_4_3 | PASS | ok | PASS | 1.000 | 0.917 | 0.957 | 7 | 0–1 |
| toy_4_4 | PASS | ok | PASS | 1.000 | 1.000 | 1.000 | 9 | 0–2 |
| game_G_1 | PASS | ok | PASS | 1.000 | 1.000 | 1.000 | 4 | 0–1 |
| game_G_2 | PASS | ok | PASS | 0.947 | 0.119 | 0.212 | 37 | 0–1 |
| **aggregate** | **12/12** | **12/12** | **12/12** | 0.902 | 0.896 | 0.865 | 8.4 | 44 PNGs |

Reading the lower Lane-2 cases: the references group outcomes differently (e.g. the
G.2 reference collapses the 36 die pairs into 3 outcomes), so a valid, richer model
scores low *precision* on the feature-multiset fallback — a representation-granularity
difference, not an error. All 12 candidates pass Lane 1, Lane 3 and the pipeline's
overall gate.

## Transition graphs

The transition graphs are drawn from each model directly:

- **`full_<case>.png`** — all states+edges, blue = initial, orange = terminal,
  edge labels `player:action@p` (merged when several joint actions share an edge).
- **`depth_<d>.png`** — the subgraph inside the BFS ball of radius `d` from the
  initial support, one image per step: "as many steps as needed" per case (up to 4
  for `toy_2_1`, 3 for `toy_3_2`, 2 for the product-state toys, 1 for the
  single-step games and dice).

## Reproduce

```powershell
python json_generation/author_v3_json_track.py       # (re)generate the candidates
python json_generation/evaluate_v3_json_track.py     # lanes 1/2/3 + graphs + summary
```