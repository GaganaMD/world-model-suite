# Final-study preflight

Run from the repository root:

```text
python experiments/physical_ai_subset/final_study/prepare_protocol.py
python experiments/physical_ai_subset/final_study/preflight.py
python -m pytest -q
```

The preflight is fail-closed: it checks canonical scenario IDs (including
`P4b_COLLISION_RISK_TRADEOFF`), five rendered prompt hashes, five reference
identities, exactly 30 unique matrix cells, P4b risk `.5`, and absence of pilot
rows. It performs no hosted calls and creates no model outputs.
