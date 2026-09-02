# Physical-AI prompt audit

The generation prompt is generation-ready but not executed. It supplies only
the scenario, canonical action vocabulary, output schema, probability rules,
terminal representation, and machine-readable state features. It does not leak
reference transitions, state/edge counts, optimal policies, or evaluation
scores. Exact action identifiers are required so action alignment is guaranteed
by construction; objective predicates remain external to generated rewards.
