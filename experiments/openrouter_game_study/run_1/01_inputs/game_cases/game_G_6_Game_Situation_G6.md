## Game Situation G.6: Silent Auction — Two Bidders, One Item

### LLM Input

Two bidders each submit a single sealed bid for an item. The higher bid wins the item; ties are broken by a coin flip. Each bidder privately values the item at either low or high, but their value is unknown to the other.

### Expected LLM Output

**Note on schema complexity.** This is a **Bayesian game**: each player has a private type (value), which is not observed by the other player. A minimal tractable model fixes two value levels (low / high) for each player and two bid levels (low / high) matching those values, yielding a 2×2×2×2 type-and-action space. The outcome depends jointly on bids (not types), but types determine rational incentives.

Because a tie is broken by a coin flip (0.5/0.5), some joint-bid outcomes are stochastic — rewards attach to outcome states (reward-on-arrival) for those cases.

For compactness the expected output models **bids only** (the private types drive strategy but are not modeled explicitly as states here — that is an acceptable simplification at this schema level). An answer that does model types explicitly is also acceptable.

```json
{
  "players": [
    { "id": "bidder_1", "description": "The first bidder, with private value unknown to bidder 2" },
    { "id": "bidder_2", "description": "The second bidder, with private value unknown to bidder 1" }
  ],
  "initial_state": "s0",
  "states": {
    "s0": { "description": "Both bidders are preparing their sealed bids; no bids submitted yet.", "terminal": false },
    "s1": { "description": "Bidder 1 submitted the higher bid and wins the item.", "terminal": true, "reward": { "bidder_1": 1, "bidder_2": 0 } },
    "s2": { "description": "Bidder 2 submitted the higher bid and wins the item.", "terminal": true, "reward": { "bidder_1": 0, "bidder_2": 1 } },
    "s3": { "description": "Both bids are equal; a coin flip decides the winner.", "terminal": false },
    "s4": { "description": "Tie broken: Bidder 1 wins the item.", "terminal": true, "reward": { "bidder_1": 1, "bidder_2": 0 } },
    "s5": { "description": "Tie broken: Bidder 2 wins the item.", "terminal": true, "reward": { "bidder_1": 0, "bidder_2": 1 } }
  },
  "actions": {
    "s0": {
      "bidder_1": ["bid_low", "bid_high"],
      "bidder_2": ["bid_low", "bid_high"]
    },
    "s3": {
      "nature": ["flip"]
    }
  },
  "transition_probabilities": {
    "s0": {
      "bid_low+bid_low":   { "s3": 1.0 },
      "bid_low+bid_high":  { "s2": 1.0 },
      "bid_high+bid_low":  { "s1": 1.0 },
      "bid_high+bid_high": { "s3": 1.0 }
    },
    "s3": {
      "flip": { "s4": 0.5, "s5": 0.5 }
    }
  }
}
```

### Judging Criteria

A good answer should include:

* exactly two symmetric bidders with private (unobserved) values acknowledged as a feature of the setting;
* two bid actions each — the model must infer a discrete bid space since the prompt does not enumerate bids;
* correct winner determination: higher bid wins outright; equal bids go to a tie-breaking random step;
* the stochastic tie-break modeled explicitly (0.5/0.5), not resolved arbitrarily to one winner;
* non-negative, non-zero-sum payoffs — the item is won, not transferred from a loser (unlike RPS), so the loser's payoff is 0, not −1, unless the model explicitly includes bid costs;
* a two-stage structure (bid → tie-break if needed).

A good answer should NOT include:

* treating it as zero-sum (loser pays −1) unless bid costs are explicitly modeled;
* omitting the tie case or resolving it deterministically;
* assuming both players know each other's valuation;
* inventing bid amounts, reserve prices, or item identity the prompt never states;
* a story.
