# Physical-AI contract pilot v2

## Design and preflight

Three P4 generations were authorized: one each from `openai/gpt-5.6-sol`,
`anthropic/claude-opus-5`, and `meta-llama/llama-3.3-70b-instruct`. The audited
prompt was used unchanged. Preflight passed: clean branch, P4 reference
self-match F1=1.0, and 91/91 tests.

## Results

All 3/3 provider requests returned content. All 3/3 passed the static contract
checker. GPT-5.6 Sol and Claude Opus 5 produced executable rollouts and passed
Lane 1 (2/3); Llama passed the static checker but its `transition()` returned an
empty distribution for both canonical actions, so rollout/Lane 1 failed (1/3).

The two executable candidates had structural F1 `0.9538` each (not exact).
Planning eligibility was `0/3`: the canonical rollout contains state IDs and
rewards but no externally verifiable `success`/`unsafe` state predicates, so we
do not infer them from names or generated reward scales. Planning regret, policy
agreement, collision deltas, and risk-probability error are therefore NA.

## Manual discrepancy audit

- GPT: no contract discrepancy; finite executable model, non-exact topology.
- Claude: no contract discrepancy; finite executable model, non-exact topology.
- Llama: mechanical transition failure (empty distribution), not a provider or
  evaluator failure.

## Decision

**CONTRACT VALIDATED, WITH CAVEAT.** The scaffold solved the prior interface
failure (old Lane-1 rate 0/6; new rate 2/3), but the prompt must additionally
make the transition fallback and externally machine-readable P4 predicates
explicit before the full 24-call study. Do not launch those calls yet.
