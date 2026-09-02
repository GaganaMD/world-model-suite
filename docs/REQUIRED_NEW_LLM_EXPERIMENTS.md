# Required new LLM experiments

No hosted calls were launched. The following generations are required only after the no-call pipelines are reviewed:

| Experiment | Cases | Models | Samples/case | Total generations | Required? | Priority |
|---|---:|---:|---:|---:|---|---|
| Symbolic embodied subset | 4--8 | Existing five | 3 | 60--120 | yes | P1 |
| Long-horizon stress | H=2,4,6,8,10 | Existing five | 3 | 75 | yes | P1 |
| G1--G9 planning alignment | only cases with audited reward/action mapping | Existing five | preserved runs first | 0 new initially | conditional | P0 |
