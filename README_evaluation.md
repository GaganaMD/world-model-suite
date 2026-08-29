# Evaluation: Lane 1 & Lane 2 (v2 schema)

Structural evaluation of LLM-generated world models. All code targets the **v2 schema**
(`players`, `initial` as a prior list, `states` as a list with `turn`/`by`/`next`).

## Files

| File | What it is |
|---|---|
| `lane1.py` | **Lane 1: mechanical checks.** Fully automated validity: positive probabilities summing to 1 (tolerance 1e-3 for rounding), transitions to declared states, complete action profiles, reachability, path-to-terminal. Runs on any model, no ground truth needed. |
| `gm_convert.py` | **Schema converter.** Turns a v2-schema model into the format `game_matching` expects: unrolls cycles to a finite horizon, handles the prior over initial states. |
| `lane2.py` | **Lane 2: structural comparison.** Scores a model against a reference *up to renaming* via `game_matching`; returns coverage + precision (harmonic mean). Imports `gm_convert.py`. |
| `reference_models.json` | The 12 reference models with a ground truth (toy 1.1–4.4, game G.1, G.2), in v2 schema. |
| `notebooks/evaluation.ipynb` | Runnable notebook: both lanes on all 12 cases, with the 17-mutation Lane 1 self-test. Self-contained (clones `game_matching`). |

## Dependencies

Lane 2 needs Jobst's `game_matching` on the path:
```
git clone https://github.com/mensch72/game_matching.git
```
Then `import lane2_v2` works from the same directory (it finds `gm_convert_v2` and `game_match`).

## Status

- Lanes 1 and 2: implemented and validated on the 12 reference-model cases.
- Lane 3 (coverage/bias for the situational cases): specified, in progress (see the annotation template).

## OpenRouter five-model game run

The OpenRouter runner executes every game case (G1--G9) against the configured
models and stores generated source, validation results, rollouts, graphs, prompts,
and a combined `summary.json` beneath one timestamped `experiments/openrouter/`
directory.

1. Put the API key in `.env`: `OPENROUTER_API_KEY=sk-or-v1-...`
2. Optionally copy/edit settings from `.env.example`.
3. From the repository root, run:

```powershell
python experiments/run_openrouter_game_experiments.py
```

The default set is GPT-5.6 Sol, Claude Opus 5, Llama 3.3 70B Instruct,
Qwen3.8 27B, and DeepSeek V4 Flash 0731. One sample across nine cases is 45 paid
API calls; change `OPENROUTER_SAMPLES_PER_CASE` deliberately before a larger run.
