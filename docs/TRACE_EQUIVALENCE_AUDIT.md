# Trace-equivalence audit

We implemented a conservative bounded trace comparison (`H=3`) that groups
action sequences by terminal status and compares discrete outcome probabilities
using total variation distance. State identifiers are ignored, but action
identifiers are intentionally exact; therefore this complements, rather than
replaces, the permutation-aware structural matcher.

Applied to the six originally ambiguous cases: 3 (Claude G1, all runs) are
behaviorally equivalent at H=3 (9/9 common traces, terminal agreement 1.0,
TV 0); 3 have no common exact action sequences and remain unresolved because
their action vocabularies/state factoring differ. None is labeled behaviorally
different solely from this conservative test.

This result is useful but limited: action renaming and state refinement require
a separately validated semantic alignment. It should not be used to increase
structural F1 or to claim semantic equivalence.
