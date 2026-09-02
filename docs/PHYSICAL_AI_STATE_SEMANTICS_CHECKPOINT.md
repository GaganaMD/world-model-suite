# Physical-AI state-semantics checkpoint

## Salvage audit

Neither executable v2 candidate is strictly evaluable for P4 external
objectives. GPT and Claude expose arbitrary string state IDs and reward values,
but no independent machine-readable goal/collision/location predicates. Under
the pre-specified rule, both are `NOT EXTERNALLY EVALUABLE`; no candidate-
specific name or reward inference is used.

## New rule

Future candidates must implement `state_features(self, state)` and satisfy the
P1--P5 schemas. External predicates in `src/evaluation/physical_features.py`
then determine success, failure, and unsafe status. Generated rewards are
excluded from the primary objective.

## Next pilot

Prepare exactly three calls (P4 × GPT-5.6 Sol/Claude Opus 5/Llama 3.3 70B,
one each), but do not launch them in this task. The success criterion is at
least 2/3 first-pass Lane-1 valid **and** strict planning eligible.
