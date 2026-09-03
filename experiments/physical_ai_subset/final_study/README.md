# Clean Physical-AI Final Study

This directory is the frozen, no-call staging area for the 30-sample study:
P1–P5 × three fixed models × two generations. It tests executable symbolic
world models, not real robotic deployment.

The fixed pipeline is provider → contract → feature contract → Lane 1 →
structural metrics → eligibility → generated planning → policy transfer →
reference-world value/regret. See `protocol.json` and
`docs/PHYSICAL_AI_FINAL_STUDY_PROTOCOL.md` for the complete preregistration.

P4b action-value decomposition records `p_gen`, `Q_safe`, `Q_risky`, and
`Q_gap` together; generated rewards never define the external objective.
Invalid stages produce `NA`, with no retries or repairs. Earlier pilot/debug
outputs are excluded. Reproduction uses the repository test suite and existing
offline evaluators; no API calls are made by the preparation commands.

**Call accounting: 30 fresh calls required.**
