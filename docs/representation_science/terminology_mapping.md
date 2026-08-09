# Terminology Mapping

## Purpose

Different research communities study similar questions with different vocabulary. This mapping is intended to reduce translation errors when connecting explicit world-model evaluation to adjacent work.

## Repository Evidence

The repository code uses the vocabulary of players, states, actions, transition probabilities, rewards, terminal states, mechanical validity, structural matching, coverage, and precision.

The executable code directly supports renaming invariance through Lane 2. It does not directly implement abstraction, refinement, bisimulation, ontology evolution, or metric invariance beyond renaming.

## Literature

| Community | Term | Meaning | Closest analogue in this project | Potential relevance | Key references |
|---|---|---|---|---|---|
| Repository code | Mechanical validity | Internal well-formedness of the generated JSON model | Lane 1 pass/fail and `min_score` | Necessary first gate before semantic evaluation | Notebook Lane 1 code |
| Repository code | Coverage | Fraction of reference structure recovered by candidate | Missing-state/action/transition sensitivity | Distinguishes omission from overall failure | Notebook Lane 2 code |
| Repository code | Precision | Fraction of candidate structure justified by reference | Unsupported extra-state/action/transition sensitivity | Distinguishes invention from omission | Notebook Lane 2 code |
| Graph algorithms | Isomorphism | Same graph structure under relabeling | Renamed world model with same structure | Already implemented in spirit by `game_matching` | Babai 2016 |
| Graph algorithms | Graph matching | Approximate alignment of graph elements | Lane 2 state/action/player correspondence | Useful for non-identical models | Jobst `game_matching`; graph kernel literature |
| Network science | Node-splitting invariance | Metric unaffected by splitting a node into equivalent subnodes | State-splitting invariance | Direct analogue for granularity-sensitive metrics | Heitzig et al. 2011/2012 |
| Network science | Graph coarsening | Reducing graph size while preserving selected properties | Merging world states or action branches | Helps think about compact models | Loukas 2019; graph coarsening literature |
| Formal methods | Abstraction | Removing detail while preserving properties of interest | Coarse world model | Clarifies what the model must preserve | Cousot and Cousot 1977; Giunchiglia and Walsh 1992 |
| Formal methods | Refinement | Adding implementation detail while preserving abstract behavior | More detailed world model | Closest general term for progressive detail | Abadi and Lamport 1991; Clarke et al. 2003 |
| Formal methods | CEGAR | Refine abstraction when a counterexample shows it is too coarse | Refine model when metric or reviewer finds missing content | Strong analogue for iterative metric-guided refinement | Clarke et al. 2003 |
| Formal methods | Simulation | One system can match another's behaviors one way | Candidate covers reference behavior | Relates to asymmetric coverage | Process algebra and verification literature |
| Formal methods | Bisimulation | Two systems match each other's observable behavior | Behavioral equivalence of states/models | Candidate for equivalence beyond naming | Milner; Givan et al. 2003 |
| Reinforcement learning | State abstraction | Grouping states while preserving chosen structure | Merging or factoring world-model states | Helps distinguish value-, policy-, and model-preserving abstractions | Li, Walsh, and Littman 2006 |
| Reinforcement learning | MDP homomorphism | Structure-preserving map between MDPs | Map from detailed to coarse world model | Useful for abstraction/refinement transformations | Ravindran and Barto |
| Reinforcement learning | Bisimulation metric | Distance between behaviorally similar MDP states | Smooth distance between states/models | May support graded equivalence | Ferns, Panangaden, and Precup |
| Reinforcement learning | Options | Temporally extended actions | Multi-step action decomposition | Relevant to action granularity | Sutton, Precup, and Singh 1999 |
| Planning | Hierarchical planning | Planning with abstract and concrete levels | Coarse-to-fine scenario model | Relevant to representation levels and horizon | Knoblock 1994 |
| Planning | Merge-and-shrink | Build abstractions by merging states and shrinking transition systems | Controlled state coarsening | Relevant to state-space compression | Helmert et al. |
| Causal modeling | Causal abstraction | Mapping between low-level and high-level causal models | Coarse/fine transition models preserving action effects | Helps reason about interventions and action consequences | Rubenstein et al. 2017; Beckers and Halpern 2019 |
| Knowledge representation | Ontology | Classes and relations for a domain | World-model schema and implicit entity types | Clarifies actors, stakeholders, objects, norms | OWL; KR textbooks |
| Ontology engineering | Ontology quality | Criteria such as clarity, consistency, completeness, conciseness | Schema adequacy and annotation quality | Prevents adding fields without quality rationale | OntoClean; OntoQA; OQuaRE |
| Ontology engineering | Ontology evolution | Controlled change to ontology over time | Adding stakeholders, beliefs, norms, institutions | Relevant if schema evolves across benchmark versions | Stojanovic; ontology change literature |
| Knowledge graphs | KG refinement | Correcting, completing, or enriching graph facts | Adding justified world-model elements | Helps separate missing content from unsupported additions | Paulheim 2017 |
| Knowledge graphs | Completeness | Whether all relevant facts are included | Reference coverage or expected-ingredient coverage | Important for open cases without canonical JSON | KG quality literature |
| Knowledge graphs | Correctness | Whether represented facts are true/supported | Candidate precision and forbidden-content checks | Direct analogue for unsupported invention | KG quality literature |
| Psychometrics | Measurement invariance | A metric measures the same construct across groups/forms | Same world-model quality score under representation variants | Useful caution for comparing models across scenario types | Meredith 1993; Millsap 2011 |
| ML representation analysis | Representational similarity | Compare learned representations under transformations | Compare explicit representations under mappings | Useful analogy, less direct than graph/formal methods | Kriegeskorte et al. 2008; Kornblith et al. 2019 |
| AI evaluation | Construct validity | Metric measures the intended capability/construct | Does Lane 2 measure representation quality or only graph similarity? | Essential for future benchmark claims | General AI evaluation and psychometrics |
| World-model benchmarks | Evaluation target | What property of a world model is being assessed | Validity, structure, uncertainty, utility | Prevents overclaiming from one score | World-model benchmark surveys |
| Semantic parsing | Underspecification | Language does not determine one formal representation | One prompt, many valid world models | Directly relevant to open situation cases | KR and semantic parsing literature |
| Database theory | Schema mapping | Transform data between schemas | Repository schema to `game_matching` schema | Already present in Lane 2 adapter | Data integration literature |
| Program semantics | Observational equivalence | No observer can distinguish systems through allowed observations | Same decision-relevant world model under allowed queries | Useful for task-relative equivalence | Process semantics literature |
| AI safety | World model adequacy | Model captures relevant facts for safe decision-making | Representation quality before policy choice | Helps connect stakeholder/uncertainty omissions to risk | World-model and decision-support literature |

## Inference

The same project concern can be phrased in multiple ways:

- "Is this larger model still the same?" becomes refinement equivalence, graph matching, state abstraction, or semantic equivalence depending on community.
- "Did the model add useless detail?" becomes over-refinement, unsupported invention, redundancy, or conciseness.
- "Did the model leave out important uncertainty?" becomes epistemic collapse, incomplete representation, or loss of decision-relevant distinction.
- "Can we stop refining?" becomes metric stabilization, abstraction adequacy, or counterexample-free refinement.

## Speculation

The most useful shared vocabulary may be transformation-based. Instead of asking for a correct granularity directly, future work can ask how metrics should behave under transformations such as renaming, state splitting, state merging, action decomposition, horizon extension, stakeholder addition, and uncertainty factoring.

## Open Questions

- Which community's notion of equivalence is closest to the repository's evaluation goals?
- Which terms should become project-standard vocabulary?
- Which terms are misleading because they imply rewards, policies, or complete ground truth?
- Should "refinement" include adding stakeholders and uncertainty, or only splitting formal states?
- Should "abstraction" be defined relative to structure, semantics, or decision relevance?

