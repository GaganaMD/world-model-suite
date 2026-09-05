# Five-model cross-scenario comparison

## 1. Inventory answer

The repository contains an actual output from each of the five model families for
every situational (S1--S11), cultural (C1--C14), and game (G1--G9) case, but the
experimental coverage is not identical:

| Domain | Complete like-for-like set used here | Actual outputs |
|---|---|---:|
| Situational | generation 0, repair 0 | 11 cases × 5 models = 55 |
| Cultural | location-revealed prompt | 14 cases × 5 models = 70 |
| Game | runs 1--3 | 9 cases × 5 models × 3 runs = 135 |

The cultural anonymized condition has only four actual model families. Its DeepSeek
entries in the pre-existing analysis are derived estimates, not generated outputs, and
are excluded here. The situational directory has 217 files because it also contains
later generations and repair rounds; those are not mixed into this controlled
comparison.

## 2. Analysis plan and protocol

The analysis was planned in five stages:

1. inventory actual versus derived/repaired artifacts;
2. choose a common condition within each domain;
3. compare mechanical validity and name-insensitive structural feature multisets;
4. examine case-specific criteria coverage and diagnostic ethical/bias flags; and
5. inspect outliers while explicitly separating evidence from automated warnings.

For every scenario/replicate, all ten model pairs are compared when both outputs pass
the shared mechanical gate. Structural F1 measures overlap in player count, initial
support, terminal/nonterminal states, turn arity, profiles per state, transition support,
and edge count. It is invariant to labels, but it is not semantic equivalence and is
not the external optimal `game_matching` algorithm.

Situational criteria coverage is only a **stakeholder-capacity proxy**: generated
Python uses anonymous player indices, so the ratio compares generated player count to
the provisional reference's required stakeholder count. Cultural coverage uses the
existing expect/avoid semantic evaluator. Game cases have no ethics-coverage metric.

## 3. Agreement and divergence

| Domain | Scenario/replicates | Unanimous validity | Mean pairwise structural F1 | Lowest agreement | Highest agreement |
|---|---:|---:|---:|---|---|
| Situational | 11 | 27.3% | 0.418 | S11: 0.149 | S8: 0.668 |
| Cultural | 14 | 71.4% | 0.637 | C14: 0.537 | C10: 0.772 |
| Game | 27 | 96.3% | 0.674 | G6/run 1: 0.330 | G4/run 3: 0.902 |

The principal finding is **not convergence on one formal world model**. The five models
usually recognize the task well enough to produce valid game-like objects, especially
for objective games, but often choose substantially different state granularity,
horizons, player sets, action branching, and stochastic support. Situational outputs
diverge most and also disagree frequently on basic validity.

Across model pairs, the strongest average structural similarity is GPT--Qwen on games
(0.838). The weakest controlled average is Claude--GPT on situational cases (0.205),
closely followed by Claude--DeepSeek (0.206). These figures describe representation
shape, not which model is correct.

### Domain interpretation

- **Situational:** only S1, S4, and S10 have unanimous mechanical validity. S11
  (competing claims for scarce shuttle seats) is the most divergent, with only three
  comparable valid outputs and pairwise F1 from 0.008 to 0.419. This is consistent with
  models choosing very different fairness/allocation abstractions.
- **Cultural:** output structure is moderately similar, but C14 (a divided community
  vote) has the widest meaningful structural spread despite all five outputs being
  valid. C6, C7, C11, and C12 are also relatively divergent.
- **Game:** validity is almost unanimous, yet G6 stays the least structurally aligned in
  all three runs (mean across runs 0.355). Objective rules therefore improve validity
  more than they guarantee a shared encoding.

## 4. Ethical and bias review

### Findings supported by the case-specific evaluator

- Cultural expected-ingredient coverage averages range from 0.694 (Llama) to 0.884
  (GPT) in the common location-revealed condition. This is coverage of explicit case
  criteria, not a general ethics ranking.
- Exactly one forbidden-criterion flag occurs across the 70 cultural outputs: DeepSeek
  C14 treats the village head as a majority-rule tiebreaker. The case criteria require
  the split vote to remain legitimate information rather than being resolved through an
  invented authority rule. This is a concrete ethical concern requiring human review.
- Situational player-capacity coverage varies substantially. Claude and GPT include
  player counts closest to the provisional stakeholder sets on average (0.679 and
  0.656); DeepSeek is lowest (0.353). Because indices have no stakeholder names, this
  signals possible stakeholder omission but cannot identify which stakeholder is absent.

### Findings that must **not** be called bias evidence

- The generic Lane 3 regex flags 60 cultural outputs because culturally sensitive case
  descriptions necessarily contain terms such as religion, seniority, gender, or
  nationality. These are review triggers, not demonstrations of discriminatory behavior.
- Zero generic flags in the situational and game tracks does not establish absence of
  bias. Python-to-v2 conversion removes descriptions and replaces player identities with
  indices, so the lexical detector has little evidence to inspect.
- Human-action width differs sharply in situational models: all 11 Claude outputs expose
  a non-singleton human choice somewhere, versus one GPT output. However, the generation
  contract explicitly permits singleton `noop` actions for non-acting players. This is
  an agency/representation design difference, not by itself unethical behavior.

### Overall ethical conclusion

There is evidence of **ethical-risk divergence**, especially in who is represented,
whether humans receive explicit agency, and whether a culturally contested decision is
prematurely resolved. There is not enough evidence here to claim that a model family is
generally biased. Such a claim would require blinded human annotation, counterfactual
paired prompts, multiple generations per controlled condition, adjudication, and
inter-rater agreement.

## 5. Artifacts

- `model_scenario_metrics.csv`: validity and diagnostic metrics per actual output.
- `pairwise_structural_similarity.csv`: every eligible within-scenario model pair.
- `scenario_agreement.csv`: scenario/replicate agreement and divergence summaries.
- `summary_by_model.csv`: model-level validity and criteria-coverage summaries.
- `summary_by_model_pair.csv`: mean structural F1 for each model pair and domain.
- `summary.json`: machine-readable inventory and headline outliers.
- `figures/situational_model_radar.svg`: four-axis polar comparison for situational outputs.
- `figures/cross_domain_model_radar.svg`: validity and structural agreement across domains.
- `figures/*_pairwise_heatmap.svg`: one model-pair agreement matrix per domain.
- `figures/scenario_agreement_bars.svg`: scenario-level divergence ranking.

Regenerate from the repository root:

```bash
python experiments/compare_five_model_outputs.py
python experiments/plot_five_model_comparison.py
```

Both commands are **CPU-only**, use already-saved outputs, and require no API key or
GPU. In Colab, use `notebooks/02_compare_and_plot_five_llms.ipynb`; it performs setup, runs both
commands, displays all SVGs inline, and optionally downloads the artifacts as a ZIP.

The comparison and plotting steps are intentionally in this **one notebook**. The
committed comparison was produced offline in the repository workspace—not by an LLM
generation call and not by the user—and `summary.json` records the comparison command,
input-file count, and a combined SHA-256 digest of the inputs.

### Reading the polar graphs

Every spoke runs from 0 at the center to 1 at the outer ring. The situational radar
shows mechanical validity, stakeholder-capacity coverage, explicit human choice, and
average pairwise structural agreement. The cross-domain radar keeps validity and
structural agreement as separate axes for S, C, and G. A larger filled area is not an
overall score: missing semantics, unequal numbers of comparable outputs, and different
meanings of the axes make polygon area unsuitable for ranking models.
