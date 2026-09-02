# P4b Pilot: Corrected Offline Evaluation

## Bug Summary

The original runner used legacy P4 during evaluation and applied an overly
restrictive location domain. Those pre-fix metrics are retained only for
provenance.

## Generation Audit

All three preserved responses used the P4b prompt. GPT and Claude are
mechanically executable; Llama has empty transition distributions.

## Pipeline Fixes

Corrected evaluation uses immutable scenario/reference/objective IDs and rejects
legacy-reference mixups. Location labels are scenario-defined strings.

## Reference Validation

P4b has `p*=2/9`, reference risk .5, safe_route, and value .6.

## Corrected Candidate Results

Structural F1 is GPT .2403 and Claude .1360; Llama is NA. These are P4b
structural diagnostics only.

## Planning Results

No candidate is reported as strictly eligible for regret because policy transfer
is not yet complete.

## Scientific Status and Final Study

Generation artifacts are valid for GPT/Claude, but this is debug evidence only
because evaluation was repaired after generation. No further calls were made;
30 clean final calls remain required.
