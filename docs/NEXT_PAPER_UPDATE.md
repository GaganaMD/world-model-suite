# Next paper update

## New completed findings

- A no-call controlled perturbation calibration now measures planning value/regret and reachability/reversibility under explicit, hand-authored POSG errors (`experiments/paper_extension_results/controlled_perturbations/results.csv`). This is a pipeline validation result, not evidence about LLM generations.
- The existing empirical paper results remain unchanged: matched Lane-1-passing game F1 mean 0.3660, median 0.1778, and 28/134 exact matches.

## Planned findings not yet supported

Generated-model planning regret, structural-F1/planning association, cross-run policy disagreement, long-horizon degradation, intervention consistency, and embodied-subset transfer require validated objectives and/or new generations.

## Manuscript changes made

No new generated-model claims were inserted. The infrastructure audit and evidence boundary are documented so the manuscript does not overclaim downstream control utility.

## Highest-value remaining experiment

Audit reward and action alignment for the preserved G1--G9 candidates, then evaluate their policies in the canonical reference environment without making new API calls.
