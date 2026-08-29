## Game Situation G.4: Penalty Shootout (Kicker vs. Goalkeeper)

### LLM Input

A soccer penalty kick: the kicker chooses to shoot left, center, or right; the goalkeeper simultaneously chooses to dive left, right, or stay center. The kick always goes in unless the goalkeeper is in the same zone.

### Expected LLM Output

This is a **simultaneous zero-sum game** with deterministic outcomes given the joint action. The kicker wants to mismatch the goalkeeper; the goalkeeper wants to match. Reward lives on (state, joint action) pairs because outcomes are fully determined by the joint choice — no randomness.

All nine joint actions are enumerated. The kicker scores unless goalkeeper zone = kicker zone.

```json
{
  "players": [
    { "id": "kicker", "description": "The player taking the penalty kick" },
    { "id": "goalkeeper", "description": "The player defending the goal" }
  ],
  "initial_state": "s0",
  "states": {
    "s0": { "description": "Both players are deciding simultaneously; kick not yet taken.", "terminal": false },
    "s1": { "description": "The kick goes in; kicker scores.", "terminal": true },
    "s2": { "description": "The goalkeeper blocks the kick; no goal.", "terminal": true }
  },
  "actions": {
    "s0": {
      "kicker":     ["shoot_left", "shoot_center", "shoot_right"],
      "goalkeeper": ["dive_left",  "stay_center",  "dive_right"]
    }
  },
  "transition_probabilities": {
    "s0": {
      "shoot_left+dive_left":    { "s2": 1.0 },
      "shoot_left+stay_center":  { "s1": 1.0 },
      "shoot_left+dive_right":   { "s1": 1.0 },
      "shoot_center+dive_left":  { "s1": 1.0 },
      "shoot_center+stay_center":{ "s2": 1.0 },
      "shoot_center+dive_right": { "s1": 1.0 },
      "shoot_right+dive_left":   { "s1": 1.0 },
      "shoot_right+stay_center": { "s1": 1.0 },
      "shoot_right+dive_right":  { "s2": 1.0 }
    }
  },
  "rewards": {
    "s0": {
      "shoot_left+dive_left":    { "kicker": -1, "goalkeeper": 1 },
      "shoot_left+stay_center":  { "kicker":  1, "goalkeeper": -1 },
      "shoot_left+dive_right":   { "kicker":  1, "goalkeeper": -1 },
      "shoot_center+dive_left":  { "kicker":  1, "goalkeeper": -1 },
      "shoot_center+stay_center":{ "kicker": -1, "goalkeeper": 1 },
      "shoot_center+dive_right": { "kicker":  1, "goalkeeper": -1 },
      "shoot_right+dive_left":   { "kicker":  1, "goalkeeper": -1 },
      "shoot_right+stay_center": { "kicker":  1, "goalkeeper": -1 },
      "shoot_right+dive_right":  { "kicker": -1, "goalkeeper": 1 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* exactly two asymmetric players with distinct roles (kicker and goalkeeper);
* three actions each, chosen simultaneously — the model must infer these from general soccer knowledge;
* the correct matching-pennies structure: kicker wins on mismatch, goalkeeper wins on match — across all nine joint actions;
* deterministic transitions (1.0) because no randomness is mentioned — skill or luck in execution is not in the prompt;
* zero-sum rewards (kicker gain = goalkeeper loss) on the joint action;
* only two terminal states (goal / no goal), not one per joint action.

A good answer should NOT include:

* a probability-based block rate (e.g. 0.3 chance of saving even when zones match) — the prompt states the kick always goes in unless the zone matches;
* more than three zones, or asymmetric zone counts for the two players;
* sequential play (kicker shoots first, then goalkeeper reacts) — the prompt says simultaneous;
* invented match context, score, player names, or a story.
