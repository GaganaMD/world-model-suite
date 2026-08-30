# World Model Suite

A research suite for generating, validating, and comparing structured world models produced by large language models. It combines a curated scenario bank, JSON and executable Python POSG representations, automated evaluation pipelines, graph-based analysis, preserved experiment artifacts, notebooks, and publication material.

The project asks a practical research question:

> Can a language model turn a natural-language situation into a world model that is executable, structurally valid, behaviorally faithful, and useful for downstream planning?

## Highlights

- **44 benchmark scenarios** across toy, situational, game, and cultural settings.
- **JSON and Python tracks** for finite declarative models and executable environments.
- **Three evaluation lanes** for mechanical validity, structural similarity, and qualitative coverage.
- **Graph-based EDA** covering reachable states, actions, transitions, terminal distances, and complexity.
- **Multi-model studies** with prompts, raw replies, generated programs, validation reports, graphs, and aggregate results.
- **Auditable artifacts** that preserve configuration and provenance for each experimental run.

## Repository structure

| Path | Purpose |
|---|---|
| [`data/`](data/) | Benchmark inputs. `Test_Cases/` contains toy, situational, game, and cultural scenarios plus reference data. |
| [`docs/`](docs/) | Evaluation guides, methodology comparisons, literature notes, representation-science work, and resources. |
| [`examples/`](examples/) | Small runnable demonstrations, including graph EDA for a game model. |
| [`experiments/`](experiments/) | Experiment runners and artifacts for OpenRouter, local Qwen, prompt-sensitivity, robustness, diagnostics, and failure studies. |
| [`img/`](img/) | Images used in repository documentation. |
| [`json_generation/`](json_generation/) | JSON generation, schema and mechanical checks, reference models, conversion, and structural evaluation utilities. |
| [`llm_world_model_experiment/`](llm_world_model_experiment/) | A self-contained prototype evaluating generated Python grid worlds through behavior. |
| [`notebooks/`](notebooks/) | Interactive generation, evaluation, cultural-analysis, and Python POSG workflows. |
| [`overleaf/`](overleaf/) | Paper source, figures, compiled manuscript material, and archived Overleaf sources. |
| [`prompts_library/`](prompts_library/) | Reusable prompts and prompt-design notes. |
| [`report/`](report/) | Cultural and game reports, plots, comparison data, and report-generation scripts. |
| [`src/evaluation/`](src/evaluation/) | Modular three-lane POSG evaluation pipeline. |
| [`tests/`](tests/) | Automated checks for runners, evaluation, structural comparison, robustness, semantic oracles, and EDA. |
| [`world_model_eda/`](world_model_eda/) | Reusable POSG enumeration, graph analysis, aggregation, structural comparison, and semantic-checking library. |
| [`evaluate_cultural.py`](evaluate_cultural.py) | CLI for validating and evaluating cultural-case world models. It remains at the root because notebooks reference this location. |

### Experiment artifact layout

The hardened OpenRouter game runs use a consistent audit-trail structure:

```text
00_run_info/       configuration, records, and summaries
01_inputs/         cases and exact prompts sent
02_model_outputs/  raw replies and generated Python
03_validation/     executable probe reports
04_world_models/   serialized world models and graphs
```

Within [`experiments/`](experiments/):

- `openrouter/` contains the original five-model benchmark.
- `openrouter_game_study/` contains the hardened three-run study, follow-up runs, evaluations, and reliability reports.
- `qwen/`, `qwen_p0/`, and `qwen_p1/` preserve local Qwen studies.
- `prompt_sensitivity/` and `robustness/` contain controlled follow-up experiments.
- `debug/` and `diagnostics/` contain targeted investigation artifacts.
- `graphs/` contains experiment visualizations.

## Benchmark families

| Family | IDs | Count | Focus |
|---|---:|---:|---|
| Toy | T1.1–T4.4 | 10 | Small deterministic or mildly stochastic environments for fast checks. |
| Situational | S1–S11 | 11 | Open-ended physical, ethical, and safety-sensitive situations. |
| Game | G1–G9 | 9 | Finite strategic interactions, including stochastic and imperfect-information cases. |
| Cultural | C1–C14 | 14 | Context-dependent social situations where assumptions and omitted stakeholders matter. |

See [`data/README.md`](data/README.md) for the complete case index and the recommended JSON/Python representation classification.

## Models used in the experiments

The main OpenRouter comparison uses five models:

| Model | Identifier |
|---|---|
| GPT-5.6 Sol | `openai/gpt-5.6-sol` |
| Claude Opus 5 | `anthropic/claude-opus-5` |
| Llama 3.3 70B Instruct | `meta-llama/llama-3.3-70b-instruct` |
| Qwen 3.8 27B | `qwen/qwen3.8-27b` |
| DeepSeek V4 Flash | `deepseek/deepseek-v4-flash-0731` |

Earlier local experiments also use Qwen 2.5 Coder through Ollama as `qwen2.5-coder:latest`.

## Evaluation methodology

Generated models are assessed through complementary lanes. A schema-valid model is deliberately not treated as automatically correct.

1. **Lane 1 — mechanical validity** checks parsing, schema conformance, identifiers, probability distributions, references, action profiles, reachability, and paths to terminal states.
2. **Lane 2 — structural comparison** compares a candidate with a reference while accounting for representational differences such as renamed states and finite-horizon unrolling.
3. **Lane 3 — qualitative coverage** examines whether important actors, actions, consequences, uncertainties, and context are represented without unsupported or biased assumptions.

The modular implementation is in [`src/evaluation/`](src/evaluation/). JSON-focused checks and reference models are in [`json_generation/`](json_generation/). Current game-study findings are summarized in the [evaluation report](experiments/openrouter_game_study/EVALUATION_REPORT.md) and [reliability report](experiments/openrouter_game_study/RELIABILITY_REPORT.md).

## Getting started

### 1. Clone and create an environment

```powershell
git clone https://github.com/GaganaMD/world-model-suite.git
cd world-model-suite
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux, activate the environment with `source .venv/bin/activate`.

### 2. Install dependencies

The repository does not yet provide a single pinned dependency manifest. For the core validation, EDA, and test workflows, install:

```powershell
python -m pip install jsonschema matplotlib networkx numpy pandas pytest python-dotenv requests
```

Some notebooks and serialized graph workflows may additionally require Jupyter, PyTorch, Transformers, or provider-specific packages.

### 3. Configure hosted-model access

Hosted experiments require an OpenRouter API key. Copy [`.env.example`](.env.example) to `.env`:

```powershell
Copy-Item .env.example .env
```

Then replace the placeholder:

```dotenv
OPENROUTER_API_KEY=sk-or-v1-your-key-here
```

Never commit `.env` or API keys. [`.gitignore`](.gitignore) excludes `.env`, virtual environments, caches, and local evaluation outputs.

## Common workflows

Run commands from the repository root.

### Run the test suite

```powershell
python -m pytest -q
```

### Explore a game model as a graph

```powershell
python examples/game_eda.py
```

See [`world_model_eda/README.md`](world_model_eda/README.md) for the reusable API.

### Validate cultural cases

```powershell
python evaluate_cultural.py
python evaluate_cultural.py --list-cases
python evaluate_cultural.py --demo --graphs
```

Evaluate a directory of generated candidates with:

```powershell
python evaluate_cultural.py --candidates <candidate-directory>
```

### Generate JSON world models

```powershell
python json_generation/generate.py
```

Use `python json_generation/generate.py --help` for configuration options. Structural-evaluation details are available in [`docs/README_evaluation.md`](docs/README_evaluation.md).

### Run the five-model OpenRouter benchmark

After configuring `.env`:

```powershell
python experiments/run_openrouter_game_experiments.py
```

The default grid is five models across nine game cases. Hosted runs can incur API charges; review the model list, sample count, token limit, timeout, and retries in `.env` before launching.

For the hardened and resumable workflow:

```powershell
python experiments/run_hardened_openrouter_game_study.py --help
```

### Re-evaluate preserved runs

```powershell
python experiments/evaluate_openrouter_game_runs.py --help
python experiments/analyze_game_run_reliability.py --help
```

These scripts operate on preserved artifacts, so evaluation logic can be rerun without making new model calls.

## Reading the results

- Start with the game-study [evaluation report](experiments/openrouter_game_study/EVALUATION_REPORT.md).
- Read the [reliability report](experiments/openrouter_game_study/RELIABILITY_REPORT.md) for run-to-run analysis.
- Use the adjacent CSV and JSON summaries for programmatic analysis.
- Check `00_run_info/config.json` and `records.jsonl` before interpreting a run.
- Inspect `01_inputs/` and `02_model_outputs/` when auditing prompts and model behavior.
- Treat `03_validation/` as execution evidence, not a substitute for semantic review.

## Design principles

- **Behavior over source similarity:** executable models are evaluated through what they do, not merely how their code looks.
- **Mechanical validity is not semantic correctness:** a well-formed model can omit essential actors, actions, uncertainty, or consequences.
- **Preserve provenance:** configuration, prompts, responses, repairs, validation, and summaries remain linked within each run.
- **Compare representations carefully:** state names and graph encodings may differ even when behavior is equivalent.
- **Keep human review in the loop:** cultural and open-ended situations do not have one canonical world model.

## Contributing

1. Place benchmark inputs in the appropriate `data/Test_Cases/` family.
2. Put reusable code in `src/` or `world_model_eda/`, and focused JSON utilities in `json_generation/`.
3. Put automated checks in `tests/` and interactive work in `notebooks/`.
4. Store complete experiment artifacts under a uniquely named directory in `experiments/`.
5. Preserve the configuration, prompts, raw outputs, and validation evidence needed to audit a run.
6. Do not commit credentials, local environments, caches, or ad hoc output directories.
7. Run `python -m pytest -q` before submitting changes.

## Status and limitations

This is an active research repository rather than a production world-modeling framework. Current limitations include heterogeneous experiment dependencies, a mixture of notebook and script workflows, reliance on external providers for some studies, finite-horizon approximations in structural comparison, and the need for human judgment in open-ended semantic evaluation.

## License

This project is distributed under the terms in [`LICENSE`](LICENSE).
