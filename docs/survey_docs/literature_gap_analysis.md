# Literature Gap Analysis

## 1. Scope and thesis

The Explicit World Models repository should not be framed primarily as a contribution to benchmark organization. Scenario taxonomies, capability scales, metadata schemas, ontology-based organization, annotation methodology, and world-model benchmark maps are already mature research areas.

The repository points toward a different scientific object:

> **The quality of an explicit action-conditioned world model generated from an underspecified natural-language situation.**

This document synthesizes the repository and four literature frameworks to identify what is established, what the repository already contributes, and what could become a defensible paper contribution.

> **Claim discipline**
>
> - **Repository evidence** means directly supported by the notebooks or tracked branch history.
> - **Literature-supported** means present in one or more cited frameworks.
> - **Inference** means a conservative interpretation of repository evidence.
> - **Speculation** means a possible future research program, not a current repository contribution.

## 2. Repository summary

The expanded notebook contains 27 scenarios across four regimes:

- ten fully or nearly fully specified toy stochastic games;
- two familiar games whose rules must be reconstructed;
- eleven underspecified social and safety situations; and
- four culturally and institutionally situated cases.

The formal output is a JSON stochastic-game model containing players, an initial state, states, state-dependent actions, transition probabilities, and optional rewards. The representation describes possibilities rather than policies or predicted behavior.

The evaluation pipeline contains:

1. **Lane 1:** automated parse, schema, and mechanical validation;
2. **Lane 2:** structural comparison with a canonical reference up to renaming, reporting coverage and precision; and
3. **Lane 3:** a proposed semantic evaluation based on expected/forbidden ingredients, bias checks, and human review.

The open-ended annotations require properties that exceed the formal schema: stakeholder coverage, preservation of uncertainty, information gathering, institutional authority, autonomy, fairness, cultural non-determinism, and avoidance of unsupported narrative detail.

This creates the repository’s most important scientific tension:

```text
What the schema can express             What the annotations require
---------------------------             ----------------------------
players                                 acting and non-acting stakeholders
states                                  observations and epistemic status
actions                                 information-seeking and authority
transition probabilities                uncertainty about facts and intentions
optional numeric rewards                norms, autonomy, fairness, and consent
terminality                              open-ended real-world continuation
```

## 3. Existing literature summary

### 3.1 AIBench Scenario

AIBench develops scenario-distilling methodology for large real-world AI services. It represents applications as DAGs of AI and non-AI tasks, constructs tractable proxy scenarios, distinguishes scenario/component/micro levels, and validates proxies against real performance behavior. Its major transferable lesson is that a benchmark scenario is a purposeful abstraction whose fidelity must be demonstrated, not assumed.

Source: [AIBench Scenario](https://arxiv.org/abs/2005.03459).

### 3.2 General capability scales

The Nature framework develops general, quantitative demand scales for benchmark items. It distinguishes elemental capabilities, knowledge, and extraneous difficulty; measures sensitivity and specificity; validates human and LLM annotations; and predicts performance across tasks. It provides a stronger basis for capability-aware benchmark analysis than an ad hoc repository taxonomy.

Source: [General Scales Unlock AI Evaluation](https://www.nature.com/articles/s41586-026-10303-2).

### 3.3 Intelligence Task Ontology

ITO provides a formal ontology and knowledge graph for AI tasks, processes, benchmarks, metrics, and reported results. It supports integration, inference, network analysis, and collaborative curation. General benchmark metadata and task hierarchies should map to this work rather than compete with it.

Sources: [ITO paper](https://arxiv.org/abs/2110.01434) and [ITO Explorer](https://openbiolink.github.io/ITOExplorer/).

### 3.4 Survey of World Model Benchmarks

The 2026 survey organizes 95 benchmarks by evaluation target, protocol, metric level, and data source. It covers visual/temporal quality, state consistency, long-horizon persistence, physical plausibility, causal reasoning, control fidelity, interactive dynamics, and functional utility. Its landscape is dominated by learned visual and embodied world models rather than explicit symbolic models induced from language.

Source: [A Survey of World Model Benchmarks](https://world-model-benchmarks.github.io/).

## 4. Comprehensive comparison matrix

| Theme | Existing literature | Repository | Gap | Opportunity |
|---|---|---|---|---|
| Benchmark methodology | AIBench provides scenario distillation and fidelity validation | Curated scenario tracks and evaluation lanes | No explicit validation of scenario representativeness | Adopt fidelity analysis; do not claim scenario methodology itself |
| Capability taxonomy | Nature supplies quantitative general scales | Capabilities implied by headings and judging criteria | Claims are not item-level or construct-validated | Annotate existing cases using established scales |
| Metadata | ITO and survey provide machine-readable schemas | Metadata mostly in titles and prose | Limited interoperability and version provenance | Map to existing standards |
| Coverage | Nature profiles demand distributions; ITO/survey map landscapes | Qualitative coverage analysis only | No measured balance or sensitivity | Use coverage as benchmark QA, not headline novelty |
| Evaluation protocol | Survey distinguishes open/closed loop and prediction/outcome evidence | Mostly open-loop generated JSON evaluation | Downstream utility is not measured | State claim boundaries explicitly |
| Annotation methodology | Nature uses anchors, multiple raters, Delphi, and agreement | Exact references and expect/avoid lists | Open-case reliability unknown | Validate semantic dimensions empirically |
| Benchmark hierarchy | Established broadly | Levels 1–4 and G/S/C tracks | Levels mix formal complexity and underspecification | Treat axes separately in analysis |
| Representation ontology | Formal methods and domain ontologies exist; ITO covers research artifacts | Minimal game ontology plus rich prose criteria | Stakeholder, evidence, norm, and belief concepts are absent formally | Study a world-model-specific ontology without recreating ITO |
| Mechanical validity | Schema/formal validation is established | Strong Lane 1 with 17 negative tests | Validity is necessary but not adequacy | Use as first layer, not headline |
| Structural fidelity | Graph matching/equivalence methods exist | Lane 2 matching up to renaming | Refinement and abstraction are not handled | Study task-relative equivalence |
| Representation quality | World-model survey measures predicted/generated dynamics | Repository separates validity, coverage, invention, and checklist adequacy | No unified construct or validated scales | Primary scientific opportunity |
| Completeness | Recall/coverage concepts are established | Lane 2 reference coverage; S/C expected ingredients | Canonical reference is unavailable for open cases | Define justified possibility coverage |
| Unsupported invention | Hallucination/precision concepts are established | Lane 2 candidate precision; S/C forbidden content | Structural extras and semantic inventions are conflated | Model support/provenance per element |
| Equivalence | Formal isomorphism/bisimulation and AIBench proxy fidelity are adjacent | Renaming equivalence only; larger valid models acknowledged | Multiple valid abstractions lack criteria | High-value paper direction |
| Uncertainty | POMDPs, calibration, and epistemic planning exist | Aleatoric probabilities plus prose-level epistemic requirements | Beliefs and observations are not first-class | Evaluate epistemic fidelity of induced models |
| Hidden information | Established in games and decision processes | Hidden coins and uncertain S/C facts | World truth and actor knowledge share one state | Separate world, observation, and belief claims conceptually |
| Stakeholders | Safety and requirements literature model stakeholders | Central in S/C annotations | Only active players are formal entities | Distinguish actors, affected parties, and institutions |
| Norms | Normative systems literature is extensive | C and S cases require norms and authority | Norms are free text and may be mistaken for rewards | Study norm-aware possibility models without policy selection |
| Institutional reasoning | Existing work covers rules and authority | Lockout, school policy, emergency procedure, hierarchy, society rules | No first-class authority or rule relation | Evaluate institutional fidelity |
| Decision relevance | Functional utility appears in survey; decision theory is established | Level 3 preserves variables that may matter under different goals | No explicit criterion for relevant abstraction | Define decision-relative sufficiency |
| Bias | Bias and fairness benchmarks are extensive | Cultural symmetry and fairness cases | Bias criteria are not validated or disentangled from knowledge | Treat as an application of representation quality |
| Multiple valid models | Formal equivalence and underspecification exist separately | Explicitly acknowledged in 2.2 and all open cases | No equivalence class or adjudication process | Central empirical object |

## 5. What already exists

The project should treat the following as methodological infrastructure rather than novelty:

1. Scenario-based benchmark construction.
2. Hierarchical organization of benchmark tasks.
3. General capability taxonomies.
4. Quantitative item-demand rubrics.
5. Benchmark coverage and balance analysis.
6. Sensitivity and specificity as construct-validity criteria.
7. Human/LLM annotation with adjudication.
8. General task, benchmark, metric, and result ontologies.
9. Open-loop/closed-loop protocol distinctions.
10. Prediction-level versus downstream-outcome metrics.
11. World-model evaluation targets such as causal reasoning, state consistency, physical plausibility, persistence, control fidelity, and utility.
12. Graph isomorphism and formal-model validation as general techniques.

Claims such as “we introduce a capability taxonomy for world models” or “we provide a hierarchical scenario benchmark” would be weak against this literature.

## 6. What the repository already contributes

### 6.1 A layered evaluation pipeline

**Repository evidence.** Lane 1 distinguishes parse, schema, and mechanical failure. Lane 2 separates structural coverage from candidate precision. Lane 3 is conceived as semantic checklist and bias review.

**Contribution status.** The combination is repository-specific, though only the first two layers have implemented evidence in the available notebook.

### 6.2 Exact-to-open ground-truth progression

**Repository evidence.** The suite moves from exact JSON, to games whose rules must be reconstructed, to open situations with expected and forbidden ingredients.

**Contribution status.** This is a useful experimental design for separating transcription, rule reconstruction, and world-model induction. It is not yet validated as a general methodology.

### 6.3 Omission and unsupported invention as distinct model failures

**Repository evidence.** Lane 2 explicitly reports coverage and precision. Open annotations separately list content that should appear and content that must not appear.

**Contribution status.** The underlying precision/recall idea is established; applying it to the possibility space of an explicit generated model is distinctive.

### 6.4 Uncertainty as a representation obligation

**Repository evidence.** Many open cases require both hypotheses to remain possible and forbid treating an observation or claim as fact.

**Contribution status.** Strong conceptual evidence, but no formal epistemic representation or metric yet.

### 6.5 Normative modeling separated from policy choice

**Repository evidence.** S.9–S.11 and C.1–C.4 require competing legitimate claims to be represented without asserting a uniquely correct resolution. The notebook elsewhere states that policies and actual behavior are outside the current model.

**Contribution status.** This separation could become important for AI safety: a policy can only reason responsibly over stakeholders and uncertainties represented by its world model.

## 7. What appears genuinely novel

Novelty labels are relative to the four reviewed frameworks and the available repository. They are not global priority claims.

### High confidence

No current feature merits a **high-confidence global novelty** claim based on this limited literature set. Mechanical checking, graph matching, scenario design, and checklists all have strong precedents.

### Medium confidence

1. **Representation-quality evaluation for language-induced explicit world models.** The repository combines formal, structural, and semantic criteria around an inspectable possibility model rather than a prediction or policy.
2. **Decision-relative equivalence under underspecification.** The repository exposes, but does not solve, the case where multiple differently sized or factored models are valid for one prompt.
3. **Semantic omission/invention trade-off for generated possibility spaces.** The task is not merely factual answer quality: missing an action removes a future branch, while invention creates unsupported branches.
4. **Epistemic fidelity as a property of a generated transition model.** Open cases require uncertainty to remain structurally live rather than merely verbally hedged.
5. **Normative option-space adequacy before reward or policy selection.** Stakeholders and competing claims must be represented before an action is chosen.

### Low confidence

1. A standalone stakeholder ontology for world models.
2. Cultural-world-model bias evaluation.
3. A given/inferred/invented label scheme.
4. Reward placement for stochastic games.

These may be valuable, but adjacent literatures are large and would require targeted review.

## 8. Potential research directions

### 8.1 Benchmark science

**Research question.** Do existing scenarios have sensitivity and specificity for the representation-quality dimensions they are intended to test?

**Motivation.** Current headings mix formal complexity, world knowledge, uncertainty, and normative reasoning.

**Novelty.** Low–medium; methodology comes from the Nature framework.

**Risk.** The work may be read as benchmark maintenance rather than a scientific contribution.

**Team overlap.** High with scenario curation. The `origin/Ani` branch contains a structured scenario corpus organized into toy, situational, game, and cultural directories, so further corpus organization would likely overlap Ani’s visible contribution. Souhaila’s role is not documented in the available repository and cannot be assessed responsibly.

**Potential paper section.** “Construct Validity of the Diagnostic Scenario Set.”

### 8.2 Representation science

**Research question.** What entities and relations must an explicit world model contain to support the repository’s open-case criteria?

**Motivation.** The formal schema contains players, states, actions, transitions, and optional rewards, while annotations require stakeholders, observations, beliefs, institutions, norms, and provenance.

**Novelty.** Medium.

**Risk.** It could become an ontology-design exercise that duplicates existing knowledge-representation work.

**Team overlap.** Low based on visible branch evidence, but team confirmation is needed.

**Potential paper section.** “The Representational Commitments of Explicit World Models.”

### 8.3 Representation quality

**Research question.** Which independent dimensions distinguish an adequate explicit world model from a merely valid one?

**Motivation.** Lane 1 proves admissibility; Lane 2 measures structural correspondence; open annotations require semantic and epistemic adequacy.

**Novelty.** High relative to the reviewed frameworks.

**Risk.** Dimensions may be correlated or unreliable unless grounded through contrastive models and expert adjudication.

**Team overlap.** Medium with Jobst’s structural matching work. It complements rather than duplicates that work if focused on where structural matching fails to capture valid refinement or semantic adequacy.

**Potential paper section.** “From Validity to Adequacy: A Layered Quality Model.”

### 8.4 World-model ontology

**Research question.** How should actors, non-acting stakeholders, observations, beliefs, norms, and institutions relate to the existing stochastic-game core?

**Motivation.** These objects are required by S/C criteria but absent formally.

**Novelty.** Medium.

**Risk.** High scope expansion and possible duplication of formal epistemic, normative, and ontology research.

**Team overlap.** Unknown for Souhaila; low based on the visible `gagana`, `main`, `Ani`, and `ethar` branches.

**Potential paper section.** “An Implicit Ontology Revealed by Evaluation Requirements.”

### 8.5 Capability-aware evaluation

**Research question.** How do general capability demands interact with world-model quality failures?

**Motivation.** A missing stakeholder could result from knowledge failure, relevance-selection failure, mind modeling, or representation failure.

**Novelty.** Medium as a bridge, low if presented as a new capability taxonomy.

**Risk.** Capability annotations may overshadow the more distinctive representation question.

**Team overlap.** Potentially high with any team member already handling annotation methodology; repository evidence is insufficient to assign ownership.

**Potential paper section.** “Separating Task Demand from Representation Failure.”

## 9. Recommended research direction

### Decision-relative adequacy and equivalence of explicit generated world models

**Research question.** When an underspecified situation admits multiple formalizations, when should two generated models be judged equivalently adequate?

**Why this direction fits the repository.** It arises directly from four existing features:

1. Lane 1 establishes that validity is insufficient.
2. Lane 2 establishes renaming-invariant structural comparison.
3. Jobst’s notebook comment recognizes that a valid model may be much larger than the reference.
4. S/C cases intentionally lack one canonical expected JSON.

**Why it complements Ani.** Ani’s visible branch contribution structures and externalizes the scenario corpus. Equivalence research uses that corpus as evidence but does not duplicate scenario extraction, organization, or benchmark packaging.

**Why it complements Souhaila.** Souhaila’s contribution is not documented in the available repository, so a precise non-overlap claim would be invented. The recommended direction should be validated with her directly. Its focus—formal and expert criteria for alternative valid representations—is sufficiently narrow to remain separable from general annotation or benchmark curation work.

**Why it aligns with Jobst’s vision.** Jobst’s comments distinguish possibilities from policies, question overly narrow canonical models, and motivate structural matching up to renaming. The proposed work treats Lane 2 as a baseline and studies the next unresolved question: equivalence beyond isomorphism.

**Why it does not duplicate the reviewed literature.** AIBench studies designer-created proxy fidelity; Nature studies item capability demands; ITO organizes task and benchmark knowledge; the world-model survey maps evaluation targets and protocols. None provides a validated criterion for whether two language-induced explicit possibility models preserve the same decision-relevant content.

**Potential major contribution.** A layered equivalence framework could distinguish:

1. exact identity;
2. renaming isomorphism;
3. behavioral equivalence;
4. abstraction/refinement equivalence;
5. epistemic equivalence; and
6. decision-relative adequacy.

The scenarios would function as diagnostic instruments for this theory rather than as the paper’s headline product.

## 10. Paper framing

The weak framing is:

> “We introduce a benchmark of 27 scenarios for testing LLM-generated world models.”

The stronger framing is:

> “We study how to evaluate explicit world representations when natural-language situations do not determine a unique formal model.”

The headline contribution should be the transition from **validity to adequacy** and from **graph identity to decision-relative equivalence**.

Candidate titles include:

- *When Is a Generated World Model Good Enough?*
- *One Situation, Many Models: Equivalence in Language-Induced World Representations*
- *Between Omission and Invention: Evaluating Explicit Models of Possible Worlds*
- *Beyond Graph Matching: Representation Adequacy Under Underspecification*

## 11. Immediate research agenda

No benchmark redesign is required. The next scientific steps are:

1. Select existing cases that already expose representational non-uniqueness.
2. Articulate multiple valid and invalid models for the same prompt.
3. Identify the exact transformation relating each pair: renaming, refinement, state splitting, horizon extension, uncertainty collapse, omission, or invention.
4. Obtain independent expert judgments about adequacy and equivalence.
5. Compare those judgments with Lane 1 and Lane 2 outcomes.
6. Determine which disagreements reveal missing quality dimensions.
7. State the limits of structural, semantic, and decision-relative claims separately.

These are research-design activities, not implementation proposals.

## References

- Gao, W. et al. [AIBench Scenario: Scenario-distilling AI Benchmarking](https://arxiv.org/abs/2005.03459).
- Zhou, L. et al. [General Scales Unlock AI Evaluation with Explanatory and Predictive Power](https://www.nature.com/articles/s41586-026-10303-2).
- Blagec, K. et al. [A Curated, Ontology-based, Large-scale Knowledge Graph of Artificial Intelligence Tasks and Benchmarks](https://arxiv.org/abs/2110.01434).
- Anonymous authors. [A Survey of World Model Benchmarks](https://world-model-benchmarks.github.io/), 2026 manuscript snapshot.
