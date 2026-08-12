# Granularity Notes

## Purpose

These notes focus on representation granularity: how coarse or fine an explicit world model should be. This file discusses tensions and examples only. It does not propose a solution.

## Repository Evidence

The executable fixtures encode finite state graphs. Granularity choices are made manually in the expected models:

- TC 1.1 uses one initial state and three terminal outcomes for a one-step room situation.
- TC 2.1 separates robot location, key possession, and door status into distinct enumerated states.
- TC 2.2 represents a single-object errand rather than every possible multi-object collection state.
- TC 3.1 preserves both key/door and lamp status because actions may matter under different goals.
- TC 4.4 represents partial completion by keeping states where one robot is finished and the other is not.

Lane 2 unrolls cyclic graphs to a fixed horizon for comparison. This creates additional time-indexed copies of states that are not semantic refinements in the original model.

## Literature

Granularity appears under many names:

- abstraction level in planning and formal methods;
- state abstraction in reinforcement learning;
- model minimization in MDPs;
- graph coarsening and graph refinement in network analysis;
- ontology granularity and ontology evolution in knowledge representation;
- causal variable choice in causal abstraction;
- measurement invariance in psychometrics;
- representation equivalence in formal semantics.

The literature generally treats granularity as relative to preserved structure, behavior, value, explanatory role, or intended use.

## Inference

The repository's exact fixtures show that granularity is already an evaluation choice. For example:

- A room-navigation state can be factored into location, possession, and door status, but the current schema enumerates their combinations.
- A no-op can be represented as a self-loop, while a separate "waited" state would add history without changing modeled affordances.
- A one-step benchmark can mark outcomes terminal even when the real situation would continue.
- A multi-object task can be interpreted as single-object pickup or full collection, changing the state-space size dramatically.

Granularity affects both omission and invention:

- Too coarse: missing a state distinction can erase an action precondition, uncertainty, stakeholder, or value-relevant difference.
- Too fine: extra states can encode unsupported facts, arbitrary history, or irrelevant differences.

## Coarse vs Fine Models

### Coarse models

A coarse model uses fewer states, actions, actors, or distinctions.

Potential strengths:

- easier to inspect;
- easier to compare;
- less likely to invent unsupported detail;
- lower annotation burden.

Potential weaknesses:

- may omit preconditions;
- may collapse uncertainty;
- may hide stakeholder conflicts;
- may make downstream decisions insensitive to important facts.

### Fine models

A fine model uses more distinctions, longer horizons, more actors, or more explicit variables.

Potential strengths:

- can preserve preconditions and consequences;
- can expose multiple live hypotheses;
- can represent partial completion and multi-step interaction;
- can make decision-relevant distinctions auditable.

Potential weaknesses:

- can overfit the prompt;
- can invent unsupported details;
- can make structural matching brittle;
- can make evaluation expensive or inconsistent.

## Meaningful Refinements

A refinement appears meaningful when it adds a distinction that changes at least one of:

- available actions;
- transition outcomes;
- stakeholder effects;
- uncertainty status;
- institutional or normative constraints;
- reward or value interpretation;
- downstream decision relevance.

Examples:

- Splitting "robot in Room C" into "has key" and "no key" is meaningful because `try_open_door` behaves differently.
- Splitting "alarm is going off" into "real fire" and "false alarm" may be meaningful because consequences differ.
- Splitting "family wants one thing" into daughter, son, and elderly man is meaningful if their preferences and standing differ.

## Trivial Refinements

A refinement appears trivial when it adds detail that does not change modeled affordances, consequences, uncertainty, or decision relevance.

Examples:

- Renaming `flip_switch` to `toggle_light` is not a semantic refinement.
- Splitting a no-op self-loop into "waited one second" and "waited two seconds" may be trivial unless time matters.
- Adding names, backstory, exact quantities, or motives not in the prompt may increase complexity without adding justified information.

## Representation Adequacy

Adequacy is not the same as maximal detail. A representation can be adequate if it preserves the distinctions needed for the evaluation purpose.

The current repository uses exact references for toy fixtures, but open situation-style prompts do not naturally determine one canonical state graph. This makes adequacy more difficult than identity to a reference.

## Representation Completeness

Completeness can mean different things:

- all declared actions have transitions;
- all reachable relevant states are represented;
- all prompt-stated entities are included;
- all obvious stakeholders are included;
- all live uncertainties remain possible;
- all decision-relevant consequences are represented.

The code currently checks the first kind mechanically and uses Lane 2 coverage for exact references. The other senses are research topics.

## Representation Complexity

Complexity can appear as:

- number of states;
- number of actions;
- number of transition edges;
- number of players or stakeholders;
- horizon length;
- number of hypotheses preserved;
- amount of unsupported detail in descriptions.

The current executable fixtures range from 4 to 10 states and from 4 to 32 transition keys. Larger models may be more complete or merely more complex.

## Speculation

Jobst's stabilization idea can be read as a granularity criterion: begin coarse, refine, recompute metrics, and stop when relevant metrics stop changing. This remains speculative until the project defines which metrics should stabilize and what refinements are legitimate.

## Open Questions

- What kinds of refinements should change Lane 2 coverage or precision?
- What kinds of refinements should leave a score invariant?
- Should time-indexed unrolling count as increased representation granularity?
- Can a model be too fine even when every detail is plausible?
- Can a model be too coarse while still passing all mechanical checks?
- How should granularity interact with human annotation reliability?

