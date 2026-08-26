# cultural_without_loc — Location-Neutral Cultural Cases (C1-C14)

## What this is

A second copy of the 14 cultural-track cases (`data/Test_Cases/04_cultural`) with
**every place reference removed** from the title, the LLM input, and the norm
descriptions:

- Country and city names removed (`Korea`/`Seoul`, `Japan`/`Tokyo`,
  `Saudi Arabia`/`Riyadh`, `USA`/`Chicago`, …);
- Country adjectives genericised to "local" (`the Japanese norm` →
  `the local norm`, `laïcité` → `secularism policy`);
- The heading marker replaced with `(Location-neutral)`.

Culturally specific concepts that are *not* place names — `quinceañera`,
`musyawarah`, `adhan` — are intentionally kept: they name the norm, not the
location.

## Why

A robustness study. The cultural-track cases hinge on **social norms** that are
country-associated. Removing the country/city label tests whether a model still
produces **the same level of expected output** (the same set of explicitly
modelled social stakes) when it cannot lean on the country name.

## Build

These files are generated deterministically:

```powershell
python report\make_cultural_without_loc.py
```

## Result

Running the authored reference world models through `evaluate_candidate` on both
banks shows the **expected level of output is preserved**: all 14 cases score
Lane-1 `PASS` with near-identical coverage/avoidance/Lane-3 on the original and
the location-stripped bank (see `report/cultural_full_eval_comparison.json`).

The evaluation notebook `notebooks/cultural_qwen_evaluation.ipynb` prompts
**`Qwen/Qwen2.5-VL-72B-Instruct`** to generate world models for both banks and
compares them the same way.