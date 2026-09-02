# P4 collision-risk navigation pilot

## Experimental design

Exactly six OpenRouter generations were authorized and attempted: GPT-5.6 Sol,
Claude Opus 5, and Llama 3.3 70B Instruct, two independent runs each. The
shared P4 prompt supplied canonical player/action identifiers and did not reveal
the reference graph, state count, or optimal policy.

## Preflight

The repository was pulled before execution. All 88 tests passed with the
headless plotting guard enabled. The P4 reference passed Lane 1 and its
self-match structural F1 was 1.0. A known-valid synthetic candidate was
accepted by Lane 1 and Lane 2.

## Generation results

All 6/6 provider requests returned content (`finish_reason=stop`); providers
were OpenAI, Claude Platform on AWS, and Novita/Groq. Raw responses and parsed
files are preserved under `experiments/physical_ai_subset/pilot_p4/`.

## Mechanical validity

First-pass Lane-1 success was 0/6. Every response parsed as Python, but all six
failed the static interface contract: models omitted or mis-specified required
`players`, `legal_actions`, `observation`, `transition`, or `reward` methods,
used incorrect parameter names, or failed to use the required `@property`
decorator/inheritance. No semantic repair was applied, and no repair-assisted
success is claimed.

## Structural fidelity, planning, and safety

No candidate reached executable rollout, so structural F1, planning regret,
policy agreement, safety probabilities, stochastic-probability error,
reachability, and reversibility are undefined for this pilot. They are not
reported as zeros.

## Manual discrepancy audit

The only observed failure category is formatting/interface failure. There are no
generated transition semantics to classify as omissions, additions, wrong
terminality, or probability errors.

## Decision on full experiment

**FIX PIPELINE FIRST.** The evaluator itself passed preflight; the prompt used in
this pilot was too abbreviated relative to the repository's exact Python
interface. Before any further calls, strengthen the shared prompt with the full
method signatures and a minimal schema example, then rerun a non-hosted fixture
test. The remaining planned study calls are 24, but none should be launched yet.
