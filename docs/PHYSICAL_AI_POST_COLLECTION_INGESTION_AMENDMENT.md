# POST-COLLECTION / PRE-OUTCOME INGESTION AMENDMENT

Generation under scientific freeze `6ce1bc5` completed in `restart_03` before
this amendment.  At amendment development time, no restart_03 raw response
was semantically inspected, parsed, or evaluated, and no scientific metric was
observed.

The frozen collection runner stores OpenRouter `message.content` as the exact
text of `raw/<candidate_id>.txt`, and records its SHA-256 plus matrix identity
in `metadata/<candidate_id>.json`.  The frozen evaluator entry point is
`evaluate_python_code(scenario_id, code, model, run)`.  The missing link was a
batch ingestion boundary from those transport artifacts to that entry point.

`final_study_v2/ingest_confirmatory.py` performs only deterministic routing:

```
metadata + raw SHA-256 + frozen matrix identity
    -> exact UTF-8 raw provider text (no extraction or repair)
    -> frozen evaluate_python_code(...)
    -> evaluator result keyed by candidate_id
```

Provider failures are recorded as unavailable and are not evaluated.  Missing
or malformed metadata, missing raw artifacts, hash mismatches, duplicate IDs,
and unexpected completion state fail closed.  The adapter does not change any
scientific evaluator component, prompt, reference, objective, feature rule,
Lane1 rule, matcher, planner, transfer rule, regret definition, or safety
definition.

The boundary was validated solely with synthetic/mock collector envelopes,
including exact-text pass-through, failure handling, provenance failures,
30-cell routing, and equality with direct calls to the frozen evaluator on
the same synthetic GeneratedPOSG text.  No additional model generation was
performed and restart_03 remained unopened during development and testing.
