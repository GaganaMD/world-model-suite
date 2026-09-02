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

Corrected initial-context transfer makes GPT and Claude strictly eligible; see
the policy-transfer section below. Llama remains ineligible.

## Scientific Status and Final Study

Generation artifacts are valid for GPT/Claude, but this is debug evidence only
because evaluation was repaired after generation. No further calls were made;
30 clean final calls remain required.

## Corrected Policy-Transfer Evaluation

The evaluator maps a unique generated initial decision context to the reference
initial context and requires the exact canonical actions; state-name equality
and structural matching are not used. GPT and Claude both select `risky_route`.
At reference risk .5, each transfers to value .225 with regret .375 and
collision probability .5. Their corrected structural F1 values are .2403 and
.1360 respectively. Llama remains invalid. These are pilot/debug results.
