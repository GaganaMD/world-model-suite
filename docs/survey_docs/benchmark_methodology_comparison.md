# Benchmark Methodology Comparison

## 1. Purpose and scope

This report compares the benchmark methodology in the Explicit World Models repository with four external frameworks:

1. AIBench Scenario;
2. *General Scales Unlock AI Evaluation with Explanatory and Predictive Power*;
3. the Intelligence Task Ontology (ITO); and
4. *A Survey of World Model Benchmarks*.

The comparison is methodological. It asks which parts of benchmark construction, organization, annotation, coverage analysis, and evaluation are already well established, and where the repository addresses a different object.

> **Evidence convention**
>
> - **Repository evidence** refers to the two notebooks in `notebooks/`, especially the expanded `Copy_of_Test_Cases (1).ipynb`.
> - **Literature comparison** summarizes the cited external source.
> - **Inference** is an interpretation supported by repeated repository patterns but not stated as a formal project claim.
> - **Open question** identifies a matter not resolved by the available repository evidence.

The local repository also contains `docs/resources.md`, which indexes private project documents and presentations. Those linked artifacts are not stored in the checkout; this report therefore does not attribute claims to them.

## 2. Repository benchmark methodology

### 2.1 Benchmark tracks

**Repository evidence.** The expanded notebook contains four distinct tracks:

| Track | Cases | Ground-truth regime | Primary purpose |
|---|---:|---|---|
| Levels 1–4 | 10 | Exact expected JSON | Test schema, state tracking, preconditions, rewards, and multi-player structure |
| Game situations | 2 | Near-exact rules and expected JSON | Require reconstruction of familiar game rules rather than transcription |
| Situational cases | 11 | Expected/forbidden ingredients | Evaluate inference from an underspecified everyday situation |
| Cultural-norm cases | 4 | Expected/forbidden ingredients | Examine culturally situated norms without unjustified stereotyping or deterministic resolution |

The notebook explicitly distinguishes transcription from construction. Levels 1–4 largely state the actions and consequences; the situational track instead supplies a bare situation and expects the model to infer stakeholders, actions, uncertainties, and consequences (expanded notebook, cells 43 and 85).

### 2.2 Evaluation lanes

```text
Generated model
      |
      v
Lane 1: parse, schema, and mechanical validity
      |
      v
Lane 2: structural comparison against reference, up to renaming
      |
      v
Lane 3: expected/forbidden ingredients, bias tests, and human review
```

**Repository evidence.** Lane 1 checks JSON validity, required fields, probability normalization, referential integrity, action-profile completeness, terminal consistency, rewards, and reachability. Its stored self-test catches 17 deliberately introduced defects (expanded notebook, cells 5–10 and 132–133).

Lane 2 uses `game_matching` after adapting the repository schema. It reports reference coverage, candidate precision, and their harmonic mean. A structurally identical model with renamed states, actions, and players receives a score of 1.0; omitted and invented structure receive lower scores (cells 11–19 and 26).

Lane 3 is described but not implemented in the available notebook. The S/C cases provide its raw annotation form through “should include” and “should not include” lists.

## 3. AIBench Scenario

### Overview

**Problem.** Real industry AI services are too large, proprietary, and operationally complex to reproduce directly, while isolated component benchmarks fail to capture end-to-end system effects.

**Main contributions.** AIBench formalizes real applications as task-dependency DAGs and distils them into smaller scenario benchmarks composed of essential AI and non-AI tasks. It distinguishes scenario, component, and microbenchmark levels.

**Methodology.** Domain partners identify critical tasks and paths; the benchmark designers retain essential components, data characteristics, and execution order while reducing implementation scale. Implemented proxies are validated against real application performance.

**Evaluation philosophy.** Fidelity is empirical: a distilled benchmark is useful if it reproduces relevant end-to-end behavior, including latency, tail latency, throughput, accuracy, and energy characteristics.

**Strengths.** It makes the relationship between a real target system and a tractable proxy explicit; it separates benchmark levels; and it validates the proxy rather than assuming representativeness.

**Limitations.** It is primarily a systems-benchmarking methodology. It assumes expert access to the source application and does not address whether an AI can infer a world representation from sparse language.

**How it differs from this project.** AIBench studies designer-led scenario distillation. The repository studies model-generated state-transition representations. AIBench asks whether a proxy workload preserves system performance; this project asks whether a generated model preserves relevant actors, affordances, uncertainty, and consequences.

Source: [AIBench Scenario paper](https://arxiv.org/abs/2005.03459) and [BenchCouncil overview](https://www.benchcouncil.org/aibench/aibench-scenario/).

## 4. General Scales Unlock AI Evaluation

### Overview

**Problem.** Aggregate benchmark scores provide weak explanations of model success and weak predictions for new tasks. Benchmarks also conflate intended capabilities with knowledge and extraneous difficulty.

**Main contributions.** The Nature paper introduces general, commensurate demand scales; a set of 18 quantitative rubrics; benchmark demand profiles; model ability profiles; and instance-level performance prediction.

**Methodology.** Each item is annotated on general demand dimensions using anchored levels from 0 to 5+. The methodology separates elemental cognitive capabilities, broad knowledge demands, and extraneous dimensions such as atypicality and volume. Human raters, Delphi adjudication, and LLM annotation are compared quantitatively.

**Evaluation philosophy.** A benchmark should have construct validity. It should be sensitive to varying levels of the capability it claims to measure and specific enough not to be dominated by unintended demands.

**Strengths.** The framework is item-level, quantitative, interpretable, empirically validated, and designed to transfer across benchmarks and model populations.

**Limitations.** It characterizes the demands of solving items and predicts success. It does not define the internal adequacy of a structured artifact produced as the answer. The authors also identify navigation, multimodal, robotics, safety, fairness, and values as extension areas.

**How it differs from this project.** The Nature framework can describe what capabilities a repository scenario demands. It does not determine whether the generated world model is mechanically valid, causally adequate, complete, unsupported, or equivalent to another representation.

Source: [Nature article](https://www.nature.com/articles/s41586-026-10303-2).

## 5. Intelligence Task Ontology

### Overview

**Problem.** AI tasks, benchmarks, metrics, models, and reported results are fragmented across rapidly growing literatures.

**Main contributions.** ITO provides a manually curated ontology and knowledge graph linking AI processes, tasks, benchmarks, metrics, and results. Its published description reports approximately 1,100 AI-process classes, 1,995 metric properties, and 685,560 graph edges.

**Methodology.** ITO uses formal ontology technologies, integration with external sources, automated inference, and collaborative expert curation. It enables hierarchical and network-based analysis of the AI research landscape.

**Evaluation philosophy.** Consistent identifiers and relations make benchmark evidence discoverable, comparable, queryable, and extensible.

**Strengths.** Large-scale coverage, machine readability, formal semantics, integration, and provenance-aware curation.

**Limitations.** ITO describes research artifacts and task relations. It does not evaluate whether a particular generated state-transition model faithfully represents a natural-language situation.

**How it differs from this project.** ITO can organize this project’s benchmark, task, and metric metadata. A repository-specific ontology would need to concern the contents and quality of explicit world models, not recreate ITO’s general benchmark ontology.

Sources: [ITO paper](https://arxiv.org/abs/2110.01434) and [ITO Explorer](https://openbiolink.github.io/ITOExplorer/).

## 6. Survey of World Model Benchmarks

### Overview

**Problem.** “World-model evaluation” covers heterogeneous targets, protocols, metrics, and data sources, making benchmark claims difficult to compare.

**Main contributions.** The survey organizes 95 representative benchmarks using four coordinates:

1. evaluation target;
2. evaluation protocol;
3. metric level; and
4. evaluation-data source.

Its targets include visual and temporal quality, spatial and state consistency, long-horizon persistence, physical plausibility, causal/counterfactual reasoning, control fidelity, interactive dynamics, and functional utility.

**Methodology.** Benchmarks are coded across overlapping target categories, open- versus closed-loop protocols, prediction- versus outcome-level metrics, and real, simulated, curated, or hybrid data.

**Evaluation philosophy.** A score is interpretable only in relation to what is evaluated, how interaction occurs, what evidence the metric provides, and where evaluation cases originate.

**Strengths.** It exposes incompatible uses of the term “world model,” separates prediction quality from downstream utility, and provides a reusable machine-readable taxonomy.

**Limitations.** The mapped landscape is dominated by visual, video, driving, game, and embodied learned models. It does not focus on explicit symbolic models induced from underspecified text.

**How it differs from this project.** The survey asks how learned world models are evaluated. The repository evaluates the construction and content of an inspectable action-conditioned representation: what entities and possibilities it contains, what it omits, and what it invents.

Sources: [survey site](https://world-model-benchmarks.github.io/) and [taxonomy snapshot](https://world-model-benchmarks.github.io/assets/benchmarks.json).

## 7. Comparative analysis

| Dimension | AIBench | Nature scales | ITO | World-model survey | Repository |
|---|---|---|---|---|---|
| Primary unit | Application workflow | Benchmark item | Task/benchmark/metric entity | World-model benchmark | Situation plus generated model |
| Main target | Systems fidelity | Capability demand and ability | Knowledge organization | Evaluation landscape | Explicit representation quality |
| Graph role | Task-dependency DAG | None required | Knowledge graph | Taxonomy relations | State-transition game graph |
| Ground truth | Real application behavior | Annotated demand levels and success | Curated ontology relations | Literature coding | Exact JSON, known rules, or checklists |
| Difficulty | Workflow/system scale | Per-capability 0–5+ demands | Not primary | Target/protocol variation | Levels and specification regimes |
| Annotation | Domain experts | Anchored rubrics, humans, Delphi, LLMs | Expert curation | Literature coding | Exact references plus expect/avoid lists |
| Coverage analysis | Scenario/task coverage | Demand distributions | Graph queries | Benchmark counts by category | Informal scenario coverage |
| Evaluation output | Performance metrics | Demand/ability profiles | Structured knowledge | Comparative benchmark map | Validity, structural coverage/precision, checklist review |
| Multiple valid outputs | Proxy implementations must be equivalent | Not central | Multiple ontology mappings possible | Not central | Explicitly unavoidable in open cases |

### Benchmark-construction comparison

| Benchmark aspect | Existing literature | Repository | Opportunity |
|---|---|---|---|
| Scenario selection | AIBench uses domain-partner input and critical-path analysis | Cases are curated as toy, game, situational, and cultural tracks | Document sampling rationale and target population of situations |
| Capability claims | Nature uses quantitative, anchored item-level demands | Capabilities are implied by headings and criteria | Annotate existing items using established demand methodology |
| Metadata | ITO and the survey provide machine-readable schemas | Metadata is mostly encoded in headings and prose | Map to existing schemas rather than invent a general ontology |
| Ground-truth regime | Literature typically separates benchmark families | Repository deliberately spans exact, reconstructed, and checklist truth | Formalize ground-truth regime as a central variable |
| Evaluation granularity | Nature emphasizes instance-level analysis | Lane 1/2 operate per model; S/C criteria operate per scenario | Preserve per-dimension profiles rather than one aggregate score |
| Construct validity | Nature tests sensitivity and specificity | Not yet demonstrated | Test whether defects affect their intended quality dimensions only |
| Evolution/versioning | ITO supports continuous curation; survey publishes snapshots | Two notebook variants show evolution but no formal version model | Add research-facing version and provenance practices later |

## 8. What we should adopt

1. **AIBench’s fidelity question.** State which real modeling problem each distilled scenario preserves and which details it intentionally removes.
2. **Nature’s item-level demand rubrics.** Use graded, anchored dimensions instead of treating a scenario as simply “uncertainty” or “multi-agent.”
3. **Nature’s construct-validity tests.** Evaluate sensitivity, specificity, and inter-rater agreement before making capability claims.
4. **ITO mappings.** Reuse standard task, benchmark, data, metric, and provenance concepts.
5. **The survey’s four coordinates.** State evaluation target, open/closed-loop protocol, prediction/outcome metric level, and data source for each evaluation claim.
6. **Profile reporting.** Preserve separate quality dimensions rather than reducing all results to a leaderboard number.

## 9. What we should not reinvent

- A generic capability taxonomy.
- A generic task/benchmark/metric ontology.
- A hierarchy whose only purpose is to label easy and hard cases.
- A new vocabulary for open-loop, closed-loop, prediction-level, or downstream evaluation.
- An unvalidated LLM-judge methodology when anchored-rubric and agreement procedures already exist.
- A broad catalog of physical, causal, temporal, spatial, or control capabilities already covered by the world-model survey.

## 10. Where the repository naturally extends the literature

**Inference.** The repository’s distinctive layer is the quality of the generated representation itself:

- Is the artifact formally admissible?
- Does it preserve stated causal structure?
- Which justified possibilities are missing?
- Which entities or transitions are unsupported?
- Does it preserve unresolved uncertainty?
- When can a larger or differently factored model still represent the same situation?

AIBench validates a designer-built proxy. Nature measures task demands. ITO organizes research artifacts. The survey categorizes evaluation practices. None supplies a complete methodology for evaluating an explicit possibility model induced from underspecified language.

## 11. Open benchmark questions

1. What population of real-world situations is the current suite intended to represent?
2. Are the levels difficulty levels, representation-complexity levels, or pedagogical stages?
3. Can claimed capabilities be varied independently through controlled contrasts?
4. How reliable are the S/C expect/avoid annotations across independent experts?
5. How should exact, equivalence-class, and checklist ground truth be reported together without implying comparability?
6. How should benchmark evolution be versioned when annotations or representation conventions change?
7. Which evaluation claims require downstream utility evidence rather than prediction-level structural evidence?
8. Can the benchmark distinguish world-model failure from knowledge failure, policy failure, and value disagreement?

## References

- Gao, W. et al. [AIBench Scenario: Scenario-distilling AI Benchmarking](https://arxiv.org/abs/2005.03459).
- Zhou, L. et al. [General Scales Unlock AI Evaluation with Explanatory and Predictive Power](https://www.nature.com/articles/s41586-026-10303-2).
- Blagec, K. et al. [A Curated, Ontology-based, Large-scale Knowledge Graph of Artificial Intelligence Tasks and Benchmarks](https://arxiv.org/abs/2110.01434).
- Anonymous authors. [A Survey of World Model Benchmarks](https://world-model-benchmarks.github.io/), 2026 manuscript snapshot.
