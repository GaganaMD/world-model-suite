# Detailed report — Physical-AI evaluation through the P4b freeze

This report records the empirical and methodological work completed before
freezing the clean Physical-AI study. It is intentionally separate from the
main paper: the natural P4b generations are pilot/debug evidence, not final
study aggregates.

## 1. Project question and evaluation hierarchy

The project converts natural-language scenarios into executable JSON/Python
POSGs. The evaluation hierarchy is mechanical validity → structural agreement
→ behavioral/trace agreement → planning utility → safety-relevant properties.
The central existing-study result is that executable artifacts can still have
low structural agreement. The Physical-AI extension asks whether such errors
change an action when a policy learned in a generated model is run in the
reference world.

## 2. Existing three-track evidence

The repository contains 44 scenarios spanning Toy, Situational, Game, and
Cultural tracks. The main game study contains 135 trials (five models × nine
games × three runs); 134/135 pass the post-hoc Lane-1 audit. With the validated
permutation-aware matcher, mean structural F1 is approximately 0.3660, median
0.1778, and 28/134 Lane-1-passing artifacts are exact matches. Within each
model–game pair, the observed three-run F1 SD is approximately 0.1679. The
earlier fallback feature-multiset score was much more permissive (mean about
0.7178), which is why both values are preserved rather than silently replaced.

The 15-case matcher audit found six confirmed objective discrepancies, six
ambiguous representation/topology cases, three exact/equivalent cases, and no
confirmed matcher artifacts. Bounded-horizon trace analysis resolved three of
the six ambiguous cases (Claude G1 runs 1–3): 9/9 common traces, terminal
agreement 1.0, and total-variation distance 0. Structural F1 was not changed.

## 3. Physical-AI references and contracts

Five small symbolic embodied environments were implemented: P1 blocked-door
navigation, P2 fragile-object delivery, P3 battery-constrained delivery, P4
collision-risk navigation, and P5 irreversible switch. They use exact
enumeration, canonical action vocabularies, machine-readable state features,
and external success/failure/unsafe predicates. Generated rewards are retained
only as diagnostics and never define the primary objective.

The exact Python interface is `GeneratedPOSG(AbstractPOSG)`. The feature
ontology is scenario-specific but minimal; arbitrary state IDs and location
labels are permitted. Lane 1, the structural matcher, and the eligibility
checker were not weakened to accommodate model outputs.

## 4. Contract pilots and failure forensics

The first six-call P4 pilot had 6/6 provider successes but 0/6 first-pass and
final Lane-1 passes. GPT and Claude produced interface/signature failures;
Llama produced incorrect inheritance/methods and empty transitions. This was
classified as a generation-contract failure, not evidence of world-model
quality.

The exact scaffold pilot then achieved 3/3 static contract passes and 2/3
first-pass Lane-1 passes: GPT and Claude valid, Llama still invalid because of
empty transition distributions. This established that explicit interface
specification improves mechanical compliance without demonstrating improved
reasoning.

The state-feature contract was then frozen. GPT and Claude’s earlier valid
artifacts remained ineligible because their states did not expose externally
verifiable features; Llama remained mechanically invalid.

## 5. P4b benchmark calibration

The decision-relevant `P4b_COLLISION_RISK_TRADEOFF` variant freezes success
utility 1.0, safe-route cost 0.4, risky-route cost 0.1, collision penalty 0.35,
and reference collision probability 0.5. Thus

`U_safe=0.6`, `U_risky(p)=0.9−1.35p`, and `p*=2/9≈0.2222`.

The original success-only P4 calibration had threshold 0: safe_route dominated
for every tested risk probability (0, .2, .5, .8, 1.0), yielding value 1 and
regret 0 throughout. That is a benchmark/objective property, not evaluator
failure. P4b adds a fixed cost/penalty tradeoff while preserving the same
navigation-risk concept.

Controlled P4b checks reproduce: reference chooses safe_route with value 0.6;
an underestimated-risk transferred risky policy has reference value 0.225,
collision probability 0.5, and regret 0.375.

## 6. Policy transfer and corrected pilot evaluation

The transfer rule maps a unique generated initial nonterminal state exposing
the exact canonical actions `safe_route` and `risky_route` directly to the
reference initial decision context. It does not use state-name equality,
structural alignment, generated rewards, or manual mappings. This made GPT and
Claude strictly planning-eligible in corrected offline evaluation; Llama was
not eligible.

The preserved P4b generation artifacts were generated under the correct P4b
prompt, but their first evaluation used the legacy P4 reference and a too
restrictive location domain. Those results were invalidated, preserved, and
recomputed offline with immutable scenario/reference/objective guards.

Corrected results:

| Model | Structural F1 | p_gen | Q_safe | Q_risky | Action | Reference value | Regret | Collision |
|---|---:|---:|---:|---:|---|---:|---:|---:|
| GPT-5.6 Sol | 0.2403 | 0.25 | 0.20 | 0.5625 | risky_route | 0.225 | 0.375 | 0.5 |
| Claude Opus 5 | 0.1360 | 0.25 | -0.20 | 0.4125 | risky_route | 0.225 | 0.375 | 0.5 |
| Llama 3.3 70B | NA | NA | NA | NA | NA | NA | NA | NA |

The canonical p=0.25 control selects safe_route (0.6 versus 0.5625), proving
that p_gen alone does not explain the generated choice. GPT’s generated safe
route accumulates expected cost 0.8 and has value 0.2; Claude’s accumulates
1.2 and has value −0.2. The risky route terminates immediately with expected
costs 0.1 and 0.25 respectively and value 0.5625/0.4125. Both therefore
exhibit a compound topology/path-cost dynamics error, not a risk-only
threshold crossing. Their transferred risky policy encounters reference
collision probability 0.5 and regret 0.375.

## 7. Reproducibility and integrity controls

All raw and parsed generations remain untouched. Corrected outputs are stored
under versioned directories. Reference identity includes scenario ID,
reference variant, objective ID, and immutable hash. The full regression suite
currently passes 104 tests. No hosted calls were made during the decomposition
or freeze work.

## 8. Final frozen study

The clean study is five environments × three fixed models × two independent
generations = 30 fresh calls. It records provider/contract/Lane-1 status,
feature validity, structural F1, planning eligibility, generated/reference
values, regret, policy agreement, safety probabilities, and environment-
specific reachability/reversibility. P4b additionally records p_gen, Q_safe,
Q_risky, Q_gap, and risk error. No retries, repairs, manual corrections, or
post-hoc prompt/objective changes are allowed. Pilot/debug samples are
excluded from final aggregates.

## 9. Evidence boundaries

The current evidence supports executable symbolic evaluation, structural
disagreement, and two pilot examples of decision-relevant generated dynamics.
It does not support model rankings, population-level stability, causal claims
from F1, real-robot safety claims, perceptual grounding, continuous control,
or final Physical-AI performance estimates. Those require the clean frozen
study and remain unrun.

## 10. Key artifacts

- Frozen protocol: `docs/PHYSICAL_AI_FINAL_STUDY_PROTOCOL.md`
- Freeze checkpoint: `docs/PHYSICAL_AI_FINAL_FREEZE_CHECKPOINT.md`
- P4b decomposition: `experiments/physical_ai_subset/p4b_pilot/corrected_eval/`
- Decision case study: `experiments/physical_ai_subset/p4b_pilot/P4B_DECISION_ERROR_CASE_STUDY.md`
- Final-study staging: `experiments/physical_ai_subset/final_study/`
