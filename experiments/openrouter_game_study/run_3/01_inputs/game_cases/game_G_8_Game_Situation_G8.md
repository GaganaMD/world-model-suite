## Game Situation G.8: Stag Hunt

### LLM Input

Two hunters can each choose to hunt a stag together or hunt a hare alone. Catching a stag requires both hunters to cooperate; a lone hunter cannot bring down a stag. A hare can always be caught alone and feeds one person. A stag feeds both hunters well if they both pursue it, but yields nothing to either if only one shows up.

### Expected LLM Output

This is the **Stag Hunt** — a symmetric coordination game with two Nash equilibria: (stag, stag) and (hare, hare). Unlike the Prisoner's Dilemma, mutual cooperation is both socially and individually optimal *if* the other cooperates; but hunting stag alone yields nothing. Payoffs are non-negative and non-zero-sum.

```json
{
  "players": [
    { "id": "hunter_1", "description": "The first hunter choosing their quarry" },
    { "id": "hunter_2", "description": "The second hunter choosing their quarry" }
  ],
  "initial_state": "s0",
  "states": {
    "s0": { "description": "Both hunters are deciding independently what to hunt; no choice made yet.", "terminal": false },
    "s1": { "description": "Both hunted stag; they cooperate successfully and both eat well.", "terminal": true },
    "s2": { "description": "Hunter 1 hunted stag alone; hunter 2 hunted hare. Hunter 1 gets nothing, hunter 2 catches a hare.", "terminal": true },
    "s3": { "description": "Hunter 2 hunted stag alone; hunter 1 hunted hare. Hunter 2 gets nothing, hunter 1 catches a hare.", "terminal": true },
    "s4": { "description": "Both hunted hare independently; each catches one hare.", "terminal": true }
  },
  "actions": {
    "s0": {
      "hunter_1": ["hunt_stag", "hunt_hare"],
      "hunter_2": ["hunt_stag", "hunt_hare"]
    }
  },
  "transition_probabilities": {
    "s0": {
      "hunt_stag+hunt_stag": { "s1": 1.0 },
      "hunt_stag+hunt_hare": { "s2": 1.0 },
      "hunt_hare+hunt_stag": { "s3": 1.0 },
      "hunt_hare+hunt_hare": { "s4": 1.0 }
    }
  },
  "rewards": {
    "s0": {
      "hunt_stag+hunt_stag": { "hunter_1": 4, "hunter_2": 4 },
      "hunt_stag+hunt_hare": { "hunter_1": 0, "hunter_2": 1 },
      "hunt_hare+hunt_stag": { "hunter_1": 1, "hunter_2": 0 },
      "hunt_hare+hunt_hare": { "hunter_1": 1, "hunter_2": 1 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* exactly two symmetric hunters deciding simultaneously and independently;
* two actions each — hunt stag and hunt hare — inferred from the prompt;
* four deterministic outcomes, one per joint action;
* the key payoff asymmetry: (stag, stag) > (hare, hare) > (stag alone) = 0, correctly capturing that a solo stag hunter gets *nothing*, not a reduced reward;
* non-zero-sum, non-negative payoffs — both players can gain simultaneously;
* two distinct Nash equilibria implicit in the structure: (stag, stag) Pareto-dominates (hare, hare) but (hare, hare) is safer under uncertainty.

A good answer should NOT include:

* zero-sum or competitive framing — hunters are not competing against each other;
* a positive payoff for hunting stag alone — the prompt explicitly states it yields nothing;
* a third "wait and see" action that the prompt never introduces;
* inventing a third animal, specific hunting location, or division of the stag as food shares;
* a story or resolved narrative.
