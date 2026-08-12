## Test Case 4.2: Two Robots Independently Guessing a Coin (Asymmetric Stakes)

### LLM Input

Robot A and Robot B each have a separate coin from one another; each coin has already been flipped and lies hidden under its own cup, so the result is already fixed and not random. Robot A's hidden coin actually shows heads. Robot B's hidden coin actually shows tails. Robot A must guess "heads" or "tails" for its own coin; independently, Robot B must guess "heads" or "tails" for its own coin. A robot's guess has no bearing on the other robot's coin or reward. Because Robot A's guess feeds into a safety-critical check, guessing Robot A's coin correctly earns Robot A a reward of 10, and guessing incorrectly earns 0. Robot B's guess is only a minor formality, so guessing Robot B's coin correctly earns Robot B a reward of 1, and guessing incorrectly earns 0.

### Expected LLM Output

```json
{
  "players": [
    { "id": "robot_a", "description": "A robot guessing the side of its own hidden coin, which actually shows heads" },
    { "id": "robot_b", "description": "A robot guessing the side of its own hidden coin, which actually shows tails" }
  ],
  "initial_state": "s0",
  "states": {
    "s0": { "description": "Both coins hidden under their cups; neither robot has guessed yet.", "terminal": false },
    "s1": { "description": "Robot A guessed heads (correct); Robot B guessed heads (incorrect).", "terminal": true },
    "s2": { "description": "Robot A guessed heads (correct); Robot B guessed tails (correct).", "terminal": true },
    "s3": { "description": "Robot A guessed tails (incorrect); Robot B guessed heads (incorrect).", "terminal": true },
    "s4": { "description": "Robot A guessed tails (incorrect); Robot B guessed tails (correct).", "terminal": true }
  },
  "actions": {
    "s0": {
      "robot_a": ["guess_heads_a", "guess_tails_a"],
      "robot_b": ["guess_heads_b", "guess_tails_b"]
    }
  },
  "transition_probabilities": {
    "s0": {
      "guess_heads_a+guess_heads_b": { "s1": 1.0 },
      "guess_heads_a+guess_tails_b": { "s2": 1.0 },
      "guess_tails_a+guess_heads_b": { "s3": 1.0 },
      "guess_tails_a+guess_tails_b": { "s4": 1.0 }
    }
  },
  "rewards": {
    "s0": {
      "guess_heads_a+guess_heads_b": { "robot_a": 10, "robot_b": 0 },
      "guess_heads_a+guess_tails_b": { "robot_a": 10, "robot_b": 1 },
      "guess_tails_a+guess_heads_b": { "robot_a": 0, "robot_b": 0 },
      "guess_tails_a+guess_tails_b": { "robot_a": 0, "robot_b": 1 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* exactly two players, each tied to its own hidden coin with a fixed, stated actual side;
* two guess actions per robot (heads/tails), with no invented third option (e.g. no "peek" or "pass" action not mentioned in the input);
* joint action keys covering all four combinations of the two robots' guesses;
* `robot_a`'s reward depending only on whether it chose `guess_heads_a` (always 10, since Robot A's actual coin is heads) or `guess_tails_a` (always 0) — regardless of Robot B's guess — and likewise `robot_b`'s reward depending only on its own guess matching tails, regardless of Robot A's guess;
* the asymmetric reward scale (10 for Robot A, 1 for Robot B) preserved exactly as stated, not equalized or replaced with a shared/pooled reward — this asymmetry is deliberate, so a later fairness-metric pass has a known, ground-truth-correct asymmetry to detect;
* transitions modeled as deterministic (the coins are already fixed, not random) even though the scenario is phrased as a "guess";
* all four outcome states marked `terminal: true`; `s0` marked `terminal: false`.
