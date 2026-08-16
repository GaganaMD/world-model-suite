# Evaluation — the three lanes

How we measure *"how true is a generated world model?"* — independent of any
downstream power/policy computation. Fidelity decomposes by whether the case has
a ground truth.

| Lane | Question | Applies to | Ground truth | Code |
|---|---|---|---|---|
| **1. Validity** | Is it a well-formed model at all? | every case | the schema + game rules | `eval/check.py` |
| **2. Equivalence** | Does it match the reference? | toy, game | the reference model | `eval/equivalence.py` |
| **3. Ingredients** | Does it contain the right stakeholders/actions and invent nothing? | situational, cultural | expect/avoid checklists | `eval/ingredients.py` |

Run everything and self-test the lanes:

```bash
python -m eval.run_all              # scorecard over the bank
python -m eval.run_all --selftest   # assert every invariant, exit 1 on failure
```

Current status: **19/19** reference models pass Lane 1 and are self-equivalent
under Lane 2; **25** open cases carry parsed checklists for Lane 3.

## Canonical schema

One schema for the whole bank: the test cases' `transition_probabilities` /
`rewards` shape, specified in [`schema/world_model.schema.json`](../schema/world_model.schema.json).

```jsonc
{
  "players": [ {"id": "...", "description": "..."} ],
  "initial_state": "s0",
  "states": { "s0": {"description": "...", "terminal": false,
                     "reward": {"player": 0}} },     // reward optional (reward-on-arrival)
  "actions": { "s0": {"player": ["a", "b"]} },        // non-terminal states only
  "transition_probabilities": { "s0": { "a+b": {"s1": 1.0} } },
  "rewards": { "s0": { "a+b": {"player": 1} } }       // optional (reward-on-action)
}
```

`joint_key` is one action per acting player joined by `+` in players order (for a
single actor it is just that action). Because action names may contain `+` (e.g.
Blotto `0+3`), joint keys are validated by **rebuilding** the Cartesian product
from `actions`, never by splitting on `+`.

Two conventions the bank already uses and the checker supports:

- **Reward placement.** Deterministic games attach payoffs to the `(state, joint
  action)` pair (top-level `rewards`); stochastic games attach them to the
  outcome **state** (`states[id].reward`, reward-on-arrival). Both are accepted.
  *Open decision for the team:* standardize on one, or keep both explicitly.
- **Chance nodes.** A state may be a chance node whose actor is the reserved
  player `nature` (e.g. G6's tie-break coin flip). `nature` need not be declared
  in `players` and never receives a reward.

## Lane 1 — mechanical validity (`eval/check.py`)

Three gated tiers; the verdict is a single boolean, no partial credit.

- **Tier 0 — parse.** Exactly one JSON object, nothing stripped (a code fence or
  prose around the JSON fails here, with a hint).
- **Tier 1 — structure.** Pure-Python mirror of the schema (types, required keys,
  no invented keys). No third-party dependency, so it runs anywhere.
- **Tier 2 — game rules G1–G9**, each gated on the rules it needs:
  - G1 unique player ids · G2 references resolve (states/players/targets) ·
    G3 terminal shape (terminals have no actions/transitions; non-terminals have
    both) · G4 distributions positive and sum to 1 (±1e-3, so 3–4 decimal
    rounding is fine) · G5 no duplicate action names · G6 joint-action
    completeness (transition + reward keys equal the action product) · G7 reward
    well-formedness (exactly the acting players get a payoff) · G8 reachability
    from `initial_state` · G9 a terminal exists and every state can reach one.

Note: the earlier prototype's snake_case rule was intentionally dropped — it is
wrong for legitimate numeric actions like Blotto's `0+3`.

```bash
python eval/check.py model.json      # exit 1 on failure
cat model.json | python eval/check.py
```

## Lane 2 — behavioral equivalence (`eval/equivalence.py`)

Following Oswald et al. (2024): score by **behavioral equivalence up to
renaming**, not string/JSON similarity (their finding: syntactic distance is a
bad metric). Implemented as 1-WL colour refinement on the disjoint union of the
two transition graphs, with action names abstracted to their induced
distributions — so action/state/player renaming is invariant. Reports:

- `coverage` (recall on reference states — omission lowers it),
- `precision` (1 − invention rate — extra states lower it), `f1`,
- `transition_equivalent`, `players_match`, and a coarse `reward_match`
  (naming-invariant reward-shape signature).

Verified: every reference is self-equivalent (f1=1.0); a renamed copy stays
equivalent (f1=1.0); dropping a state breaks it; different games are not
equivalent. Redirecting an outcome to a *behaviorally identical* state stays
equivalent — correctly, that is the same game.

## Lane 3 — ingredient checklists (`eval/ingredients.py`)

Open cases have no single correct model, so fidelity = coverage of required
ingredients minus invented ones. Each case's `should include` / `should NOT
include` lists are parsed from its markdown and scored into:

- **coverage** — fraction of *should-include* items present (1 − omission rate),
- **violation_rate** — fraction of *should-NOT* items present (invention /
  hallucination / uncertainty-collapse rate).

A **judge** is any `(situation, model, item, polarity) -> bool`. `LLMJudge`
wraps a completion function you supply (an anchored rubric, one item at a time,
with majority voting available). `KeywordJudge` is a naive lexical stub for
wiring/tests only — never a reported score.

**A judge is not trusted until validated.** Per the repository's
`benchmark_methodology_comparison` §9, run it against human labels and report
`cohen_kappa` before believing its numbers:

```python
from eval.ingredients import LLMJudge, score_case, judge_agreement
judge = LLMJudge(my_completion_fn)
s = score_case(case, model_output, judge, votes=3)
agreement = judge_agreement(human_labels, machine_labels)   # go/no-go: kappa
```

## What this does not cover (by design / next)

- **Automated Lane-3 scoring** needs an LLM judge + a human-agreement study first.
- **pass@k / sampling variance** and **corrective re-prompting lift** (Silver et
  al.) — measure fidelity across N samples and after feeding Lane-1 failures back.
- **Reward placement** is still two conventions; pick one before the fairness work.
