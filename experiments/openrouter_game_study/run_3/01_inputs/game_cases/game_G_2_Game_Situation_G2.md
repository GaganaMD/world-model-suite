## Game Situation G.2: A Dice Duel (First Stochastic Case)

### LLM Input

Two players each roll one fair six-sided die at the same time. Whoever rolls the higher number wins the round.

### Expected LLM Output

**Note on schema — this is the bank's first genuinely random outcome, and it forces a schema
choice.** In Levels 1–4 each (state, joint action) led to exactly one next state, so a reward
attached to the (state, action) pair was unambiguous. Here the single joint action `roll+roll`
leads to three possible outcomes and the payoff depends on *which* one occurs — so an
expected-reward-on-action would average to 0 and lose all information. The natural fix, used
below, is to attach the reward to each **outcome state** (reward-on-arrival); consequently the
top-level `rewards` block from Level 4 is intentionally absent here. Flag for the team:
standardize whether stochastic-game rewards live on outcome states (as here) or on
(state, action, next_state) triples.

The three outcome probabilities are the objectively correct ones for two fair dice:
Player 1 higher = 15/36, Player 2 higher = 15/36, tie = 6/36 (shown rounded below; as exact
fractions they sum to 1).

```json
{
  "players": [
    { "id": "player_1", "description": "The first player, rolling one die" },
    { "id": "player_2", "description": "The second player, rolling one die" }
  ],
  "initial_state": "s0",
  "states": {
    "s0": { "description": "Both players are about to roll; no dice rolled yet.", "terminal": false },
    "s1": { "description": "Player 1 rolled higher and wins the round.", "terminal": true, "reward": { "player_1": 1, "player_2": -1 } },
    "s2": { "description": "Player 2 rolled higher and wins the round.", "terminal": true, "reward": { "player_1": -1, "player_2": 1 } },
    "s3": { "description": "Both rolled the same number; the round is a tie.", "terminal": true, "reward": { "player_1": 0, "player_2": 0 } }
  },
  "actions": {
    "s0": {
      "player_1": ["roll"],
      "player_2": ["roll"]
    }
  },
  "transition_probabilities": {
    "s0": {
      "roll+roll": { "s1": 0.4167, "s2": 0.4167, "s3": 0.1667 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* exactly two symmetric players, each rolling one die;
* a single simultaneous action per player (`roll`), i.e. one joint action from the start state;
* recognition that the outcome is **stochastic** — the die result is random, not chosen — represented as a probability distribution over outcomes, not a deterministic `1.0` transition;
* three outcomes: player 1 higher, player 2 higher, and a **tie** (equal rolls) — the tie must not be dropped even though the prompt only says "the higher number wins";
* probabilities matching two fair dice: 15/36, 15/36, 6/36 (≈ 0.417, 0.417, 0.167), summing to 1 — stated as fractions or reasonable decimals;
* zero-sum payoffs (winner vs loser; tie pays 0) attached in a way consistent with a random outcome, i.e. on the outcome states / reward-on-arrival rather than as a single number on the `roll+roll` action.

A good answer should NOT include:

* treating the roll as a chosen action with a deterministic result (e.g. an action "roll a 6", or a single `1.0` transition straight to a win);
* omitting the tie outcome, or giving wrong probabilities (e.g. 0.5 / 0.5 with no tie);
* inventing stakes, bet amounts, extra rounds, or a re-roll-on-tie rule that the prompt never states;
* a story.

# Situational Test Cases (Situation-Only Prompts)

The Level 1–4 cases above are **toy games with (near-)ground-truth**: the prompt spells out the available actions, so the LLM is mostly *transcribing* a world model into JSON. That is useful for shaking out schema and well-formedness bugs, but it is **not the real task**. We ultimately want to hand the LLM *only a description of a situation* — not a description of a world model — and have it *come up with the world model on its own*, using its general understanding of everyday life to infer the relevant stakeholders, their plausible actions, and the possible consequences over a few steps. So the prompt must **not** enumerate players, actions, or consequences.

Two consequences for how these cases are written:

1. **Input = bare situation.** Each prompt describes a situation in a few sentences and stops. It does not list actors, actions, or outcomes.
2. **No full ground truth — judging is expect/avoid.** Modeling is partly subjective, so there is no single canonical expected JSON. Instead each case lists **what a good model should contain** and **what it must not contain** (hallucinated facts, invented specifics, story-writing, a missing key stakeholder, treating an unconfirmed claim as fact, etc.). Reviewers score against those lists.

These implement the handbook's *thought-experiment* category: situations common enough that an ordinary person understands the options and stakes without being told them — which is exactly what lets us judge whether the LLM's model is adequate.
