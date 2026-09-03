# Frozen evaluator audit

The scientific component files below are identical between pre-data freeze
`71b05f9` and collection commit `7be3908` (Git blob hashes match):

| Component | Source | Freeze/current blob |
|---|---|---|
| Lane 1 | `json_generation/lane1.py` | `1def904243ed828be315a50b4b2b74b2edbc723e` |
| Structural lane | `json_generation/lane2.py` | `2d9f6dba6234080e3230b42532e17faca840000f` |
| Features/predicates | `src/evaluation/physical_features.py` | `6a270cdde4e72e630a4d550dcc90cef43343d698` |
| Policy transfer | `src/evaluation/policy_transfer.py` | `2ccb5547fcc9f7539e030fc2b9687a15c70f5f51` |
| Finite-horizon planner | `src/planning/finite_horizon.py` | `5ec94d9be966606600de75350c499fbd4b329449` |
| Preserved P4b evaluator | `experiments/physical_ai_subset/planning_regret/evaluate_p4b_preserved.py` | `d1a7aa62260e290279c1a840c0f534fcae3ac53f` |

The pre-data commit contained tested components for Lane 1, structural
comparison, features, finite-horizon planning, and P4b policy transfer. It did
not contain a complete driver applying those components to every P1–P5 final
candidate. The collection runner therefore omitted an invocation path that
did not yet exist as a complete all-scenario evaluator; this is not merely a
missing function call.

Conclusion: **CASE B — evaluator implementation incomplete for the specified
30-cell study.** Offline evaluation would require new orchestration and likely
scenario-specific integration, so final scientific aggregates are not
produced under the frozen evaluator claim.
