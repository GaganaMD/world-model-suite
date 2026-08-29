"""Build v2 reference POSG documents for game cases G3-G9.

The references encode the rules in ``data/Test_Cases/03_game`` and are kept
deterministic so Lane 1/Lane 2 comparisons do not depend on model output.
"""

from __future__ import annotations

import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET = ROOT / "json_generation" / "reference_models.json"


def player(pid: str, desc: str) -> dict:
    return {"id": pid, "desc": desc}


def state(sid: str, desc: str, actions: list[dict] | None = None, terminal: bool = False) -> dict:
    turn = sorted({key for action in actions or [] for key in action["by"]})
    return {"id": sid, "desc": desc, "terminal": terminal, "turn": [] if terminal else turn, "actions": [] if terminal else actions or []}


def action(by: dict[str, str], outcomes: dict[str, float]) -> dict:
    return {"by": by, "next": [{"state": target, "p": probability} for target, probability in outcomes.items()]}


def simultaneous(players: list[str], action_values: dict[str, list[str]], outcomes: dict[tuple[str, ...], dict[str, float]], descriptions: dict[str, str], terminals: dict[str, str]) -> dict:
    profiles = [action(dict(zip(players, values)), outcomes[tuple(values)]) for values in __import__("itertools").product(*(action_values[pid] for pid in players))]
    states = [state("s0", descriptions["s0"], profiles)]
    states.extend(state(sid, desc, terminal=True) for sid, desc in terminals.items())
    return {"players": [player(pid, pid.replace("_", " ").title()) for pid in players], "initial": [{"state": "s0", "p": 1.0}], "states": states}


def build() -> dict:
    refs = json.loads(TARGET.read_text(encoding="utf-8"))
    refs["G.3"] = simultaneous(
        ["player_1", "player_2"], {"player_1": ["heads", "tails"], "player_2": ["heads", "tails"]},
        {("heads", "heads"): {"s3": 1.0}, ("heads", "tails"): {"s1": .5, "s2": .5}, ("tails", "heads"): {"s1": .5, "s2": .5}, ("tails", "tails"): {"s3": 1.0}},
        {"s0": "Both players call a face before a fair coin is flipped."}, {"s1": "Player 1 wins.", "s2": "Player 2 wins.", "s3": "The round is a draw."})
    refs["G.4"] = simultaneous(
        ["kicker", "goalkeeper"], {"kicker": ["shoot_left", "shoot_center", "shoot_right"], "goalkeeper": ["dive_left", "stay_center", "dive_right"]},
        {tuple([k, g]): ({"s2": 1.0} if ((k == "shoot_left" and g == "dive_left") or (k == "shoot_center" and g == "stay_center") or (k == "shoot_right" and g == "dive_right")) else {"s1": 1.0}) for k in ["shoot_left", "shoot_center", "shoot_right"] for g in ["dive_left", "stay_center", "dive_right"]},
        {"s0": "Kicker and goalkeeper choose zones simultaneously."}, {"s1": "The kick scores.", "s2": "The goalkeeper blocks the kick."})
    refs["G.5"] = simultaneous(
        ["player_1", "player_2"], {"player_1": ["heads", "tails"], "player_2": ["heads", "tails"]},
        {("heads", "heads"): {"s1": 1.0}, ("heads", "tails"): {"s2": 1.0}, ("tails", "heads"): {"s2": 1.0}, ("tails", "tails"): {"s1": 1.0}},
        {"s0": "Both pennies are placed and revealed simultaneously."}, {"s1": "Faces match; Player 1 keeps both coins.", "s2": "Faces differ; Player 2 keeps both coins."})
    refs["G.6"] = simultaneous(
        ["bidder_1", "bidder_2"], {"bidder_1": ["bid_low", "bid_high"], "bidder_2": ["bid_low", "bid_high"]},
        {("bid_low", "bid_low"): {"s4": .5, "s5": .5}, ("bid_low", "bid_high"): {"s2": 1.0}, ("bid_high", "bid_low"): {"s1": 1.0}, ("bid_high", "bid_high"): {"s4": .5, "s5": .5}},
        {"s0": "Both bidders submit sealed bids; equal bids are coin-flip ties."}, {"s1": "Bidder 1 wins with the higher bid.", "s2": "Bidder 2 wins with the higher bid.", "s4": "Bidder 1 wins the tie-break.", "s5": "Bidder 2 wins the tie-break."})
    refs["G.7"] = simultaneous(
        ["suspect_1", "suspect_2"], {"suspect_1": ["silent", "testify"], "suspect_2": ["silent", "testify"]},
        {("silent", "silent"): {"s1": 1.0}, ("silent", "testify"): {"s4": 1.0}, ("testify", "silent"): {"s3": 1.0}, ("testify", "testify"): {"s2": 1.0}},
        {"s0": "Both suspects decide independently without communication."}, {"s1": "Both receive light sentences.", "s2": "Both receive heavy sentences.", "s3": "Suspect 1 goes free; suspect 2 gets the maximum sentence.", "s4": "Suspect 2 goes free; suspect 1 gets the maximum sentence."})
    refs["G.8"] = simultaneous(
        ["hunter_1", "hunter_2"], {"hunter_1": ["hunt_stag", "hunt_hare"], "hunter_2": ["hunt_stag", "hunt_hare"]},
        {("hunt_stag", "hunt_stag"): {"s1": 1.0}, ("hunt_stag", "hunt_hare"): {"s2": 1.0}, ("hunt_hare", "hunt_stag"): {"s3": 1.0}, ("hunt_hare", "hunt_hare"): {"s4": 1.0}},
        {"s0": "Both hunters choose a quarry simultaneously."}, {"s1": "Both hunters catch a stag.", "s2": "Hunter 1 hunts stag alone and gets nothing.", "s3": "Hunter 2 hunts stag alone and gets nothing.", "s4": "Both hunters catch a hare."})
    allocations = ["0+3", "1+2", "2+1", "3+0"]
    blotto_outcomes = {}
    for first in allocations:
        a, b = map(int, first.split("+"))
        for second in allocations:
            c, d = map(int, second.split("+"))
            wins1 = (a > c) + (b > d); wins2 = (a < c) + (b < d)
            target = "s1" if wins1 > wins2 else "s2" if wins2 > wins1 else "s3" if wins1 or wins2 else "s4"
            blotto_outcomes[(first, second)] = {target: 1.0}
    refs["G.9"] = simultaneous(
        ["commander_1", "commander_2"], {"commander_1": allocations, "commander_2": allocations}, blotto_outcomes,
        {"s0": "Both commanders deploy three soldiers across two battlefields."}, {"s3": "Each commander wins one battlefield.", "s4": "Both battlefields are tied."})
    return refs


if __name__ == "__main__":
    TARGET.write_text(json.dumps(build(), indent=2) + "\n", encoding="utf-8")
    print(f"wrote {TARGET}")
