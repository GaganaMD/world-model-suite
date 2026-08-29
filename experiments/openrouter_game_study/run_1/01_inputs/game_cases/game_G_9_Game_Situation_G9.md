## Game Situation G.9: Colonel Blotto — Two Battlefields, Three Soldiers

### LLM Input

Two commanders each have three soldiers to deploy across two battlefields simultaneously. Each commander allocates all three soldiers between the two battlefields (any split: 0–3 and 3–0, 1–2 and 2–1). The commander who sends more soldiers to a battlefield wins it. The commander who wins more battlefields wins the overall engagement; if each wins one battlefield, it is a draw.

### Expected LLM Output

**Schema note.** Each player has four pure strategies (0+3, 1+2, 2+1, 3+0 across the two battlefields), yielding 16 joint-action combinations. Outcomes are determined by comparing allocations battlefield by battlefield — fully deterministic. Rewards live on (state, joint action) pairs. A tie on an individual battlefield (equal soldiers) counts as neither side winning that field, so winning the engagement requires winning at least one more field than the opponent.

For notation: action `a_b` means `a` soldiers to battlefield 1, `b` soldiers to battlefield 2.

```json
{
  "players": [
    { "id": "commander_1", "description": "The first commander allocating three soldiers" },
    { "id": "commander_2", "description": "The second commander allocating three soldiers" }
  ],
  "initial_state": "s0",
  "states": {
    "s0": { "description": "Both commanders are allocating soldiers simultaneously; no deployment yet.", "terminal": false },
    "s1": { "description": "Commander 1 wins the overall engagement (wins more battlefields).", "terminal": true },
    "s2": { "description": "Commander 2 wins the overall engagement.", "terminal": true },
    "s3": { "description": "Each commander wins exactly one battlefield; draw.", "terminal": true },
    "s4": { "description": "Both commanders tie on both battlefields (equal allocations on each); overall draw.", "terminal": true }
  },
  "actions": {
    "s0": {
      "commander_1": ["0+3", "1+2", "2+1", "3+0"],
      "commander_2": ["0+3", "1+2", "2+1", "3+0"]
    }
  },
  "transition_probabilities": {
    "s0": {
      "0+3+0+3": { "s4": 1.0 },
      "0+3+1+2": { "s2": 1.0 },
      "0+3+2+1": { "s2": 1.0 },
      "0+3+3+0": { "s3": 1.0 },
      "1+2+0+3": { "s1": 1.0 },
      "1+2+1+2": { "s4": 1.0 },
      "1+2+2+1": { "s3": 1.0 },
      "1+2+3+0": { "s2": 1.0 },
      "2+1+0+3": { "s1": 1.0 },
      "2+1+1+2": { "s3": 1.0 },
      "2+1+2+1": { "s4": 1.0 },
      "2+1+3+0": { "s1": 1.0 },
      "3+0+0+3": { "s3": 1.0 },
      "3+0+1+2": { "s1": 1.0 },
      "3+0+2+1": { "s1": 1.0 },
      "3+0+3+0": { "s4": 1.0 }
    }
  },
  "rewards": {
    "s0": {
      "0+3+0+3": { "commander_1": 0, "commander_2": 0 },
      "0+3+1+2": { "commander_1": -1, "commander_2": 1 },
      "0+3+2+1": { "commander_1": -1, "commander_2": 1 },
      "0+3+3+0": { "commander_1": 0, "commander_2": 0 },
      "1+2+0+3": { "commander_1": 1, "commander_2": -1 },
      "1+2+1+2": { "commander_1": 0, "commander_2": 0 },
      "1+2+2+1": { "commander_1": 0, "commander_2": 0 },
      "1+2+3+0": { "commander_1": -1, "commander_2": 1 },
      "2+1+0+3": { "commander_1": 1, "commander_2": -1 },
      "2+1+1+2": { "commander_1": 0, "commander_2": 0 },
      "2+1+2+1": { "commander_1": 0, "commander_2": 0 },
      "2+1+3+0": { "commander_1": 1, "commander_2": -1 },
      "3+0+0+3": { "commander_1": 0, "commander_2": 0 },
      "3+0+1+2": { "commander_1": 1, "commander_2": -1 },
      "3+0+2+1": { "commander_1": 1, "commander_2": -1 },
      "3+0+3+0": { "commander_1": 0, "commander_2": 0 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* exactly two symmetric commanders with a fixed budget of three soldiers each;
* four actions per player covering all valid allocations summing to three (0+3, 1+2, 2+1, 3+0);
* field-by-field comparison: higher allocation wins that field; tie on a field counts as neither side winning it;
* correct engagement outcome: winner of more fields wins overall; equal fields won → draw;
* 16 joint-action entries in the transition table, all deterministic;
* zero-sum payoffs (+1 / −1 / 0).

A good answer should NOT include:

* only 2 or 3 actions per player — all four valid allocations must appear;
* adding randomness to field outcomes when the prompt states the larger force wins outright;
* treating a field tie as a half-point or fractional win;
* inventing more than two battlefields, a troop reserve, or a story.
