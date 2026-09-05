# Python situational evaluation (all saved files)

## Protocol

This directory evaluates all 217 Python files in `../generated_python`, including the
164 unaided `r0` files and 53 repair-round files. Each file is executed in the existing
probe subprocess, converted to v2 only when exploration is complete and error-free,
and then passed to `src/evaluation` Lane 1, Lane 2, and Lane 3.

Lane 2 uses the newly authored criteria-derived references in
`data/reference_models/situational_provisional_v2.json`. These are explicitly
provisional rather than independent ground truth; see the audit beside that file.
`game_matching` is not installed in this environment, so Lane 2 used the evaluator's
documented name-insensitive feature-multiset fallback rather than optimal graph
matching.

## Aggregate results

| Scope | Files | Probe pass | Lane 1 pass | Lane 2 scored | Mean coverage | Mean precision | Mean combined | Lane 3 checklist pass |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| All | 217 | 161 | 154 | 161 | 0.4233 | 0.7283 | 0.4432 | 157 |
| First pass (`r0`) | 164 | 127 | 122 | 127 | 0.4276 | 0.7021 | 0.4311 | 125 |
| Repairs (`r1`--`r3`) | 53 | 34 | 32 | 34 | 0.4070 | 0.8261 | 0.4882 | 32 |

Probe statuses over all files were 161 PASS, 54 FAIL, and 2 INCOMPLETE. Seven probe
passes subsequently failed Lane 1 because the shared evaluator additionally requires
every state to have a path to a terminal or rejects an unreachable exported state.

Lane 3 is the repository's deterministic representation checklist, not a human semantic
rating: it tests descriptions, stakeholders, actions, represented consequences, and
flags lexical/action-count bias risks. A checklist pass must not be interpreted as proof
that a model faithfully captures every case-specific judging criterion.

## Artifacts

- `attempt_results.csv` / `.json`: one record per source file, including probe errors,
  repair metadata, and all lane outputs.
- `summary.json`: aggregate, first-pass, and repair summaries plus protocol metadata.
- `summary_by_case.csv`: case-level totals and Lane 2 means.
- `summary_by_model.csv`: model-level totals and Lane 2 means.

Regenerate all artifacts from the repository root with:

```bash
python experiments/evaluate_python_situational.py
```

This evaluation runs entirely on **CPU**: it executes and checks Python that is already
saved in the repository and makes no LLM/API calls. No GPU is needed. For Colab, open
`notebooks/01_evaluate_situational_posgs.ipynb` and follow its cells in order. The
committed files in this directory are already-computed results; rerun only to reproduce
or refresh them after the generated inputs change.
