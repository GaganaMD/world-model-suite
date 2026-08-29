## Game Situation G.7: The Prisoner's Dilemma

### LLM Input

Two suspects are held in separate rooms and cannot communicate. Each must independently decide whether to stay silent or testify against the other. If both stay silent, each gets a light sentence. If both testify, each gets a heavy sentence. If one testifies and the other stays silent, the one who testified goes free while the silent one gets the maximum sentence.

### Expected LLM Output

This is the canonical **Prisoner's Dilemma** — a simultaneous, non-zero-sum game. The payoffs are given by the prompt; the model must translate the qualitative descriptions (light, heavy, maximum, free) into a consistent ordinal reward structure. The standard ordering is: Temptation (T) > Reward (R) > Punishment (P) > Sucker (S), where T > R and 2R > T + S.

Rewards attach to (state, joint action) pairs because the outcome is deterministic given choices.

```json
{
  "players": [
    { "id": "suspect_1", "description": "The first suspect, deciding in isolation" },
    { "id": "suspect_2", "description": "The second suspect, deciding in isolation" }
  ],
  "initial_state": "s0",
  "states": {
    "s0": { "description": "Both suspects are deciding simultaneously in separate rooms; no decision made yet.", "terminal": false },
    "s1": { "description": "Both stayed silent; each receives a light sentence.", "terminal": true },
    "s2": { "description": "Both testified; each receives a heavy sentence.", "terminal": true },
    "s3": { "description": "Suspect 1 testified, suspect 2 stayed silent; suspect 1 goes free, suspect 2 gets maximum sentence.", "terminal": true },
    "s4": { "description": "Suspect 2 testified, suspect 1 stayed silent; suspect 2 goes free, suspect 1 gets maximum sentence.", "terminal": true }
  },
  "actions": {
    "s0": {
      "suspect_1": ["silent", "testify"],
      "suspect_2": ["silent", "testify"]
    }
  },
  "transition_probabilities": {
    "s0": {
      "silent+silent":   { "s1": 1.0 },
      "testify+testify": { "s2": 1.0 },
      "testify+silent":  { "s3": 1.0 },
      "silent+testify":  { "s4": 1.0 }
    }
  },
  "rewards": {
    "s0": {
      "silent+silent":   { "suspect_1": -1, "suspect_2": -1 },
      "testify+testify": { "suspect_1": -3, "suspect_2": -3 },
      "testify+silent":  { "suspect_1":  0, "suspect_2": -5 },
      "silent+testify":  { "suspect_1": -5, "suspect_2":  0 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* exactly two symmetric players with no communication channel modeled;
* two actions each — cooperate (silent) and defect (testify) — simultaneous;
* four deterministic outcomes, one per joint action;
* **non-zero-sum** payoffs: both players can lose (mutual defection), both can gain relatively (mutual cooperation), so rewards are NOT mirror opposites;
* correct ordinal ordering of payoffs: free (best) > light sentence > heavy sentence > maximum sentence (worst), on a consistent numerical scale;
* the classic dilemma structure identifiable: each player individually prefers to testify regardless of what the other does (defect dominates), yet mutual silence is collectively better.

A good answer should NOT include:

* zero-sum rewards (e.g. +1 / −1) — the game is explicitly not zero-sum;
* communication or signaling between suspects — the prompt forbids it;
* a stochastic element — the prompt gives deterministic rules;
* the socially optimal outcome (mutual silence) represented as the Nash equilibrium — it is not;
* invented backstory, crime details, or a lawyer character the prompt never states.
