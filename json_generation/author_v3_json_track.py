#!/usr/bin/env python3
"""Author the JSON-track world models for the zero-shot v3 prompt run.

The twelve candidates (T1.1-T4.4, G.1, G.2 — the cases `data/README.md` classifies
as JSON / Both) are authored offline, strictly following
``prompts_library/zero_shot_v3_prompt.md``: no LLM credentials are configured in
this workspace, so this script plays the generator's role deterministically. Each
model is derived from the case's own situation text; nothing is copied from the
reference models. Provenance is written to ``_manifest.json`` next to the models.

    python json_generation/author_v3_json_track.py
"""
from __future__ import annotations

import hashlib
import json
import sys
from itertools import product
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

RUN_DIR = ROOT / "runs" / "v3_json_track"
PROMPT_PATH = ROOT / "prompts_library" / "zero_shot_v3_prompt.md"
BANKS = ("01_toy", "03_game")


# ---------------------------------------------------------------- helpers (v2 builders)
def robot(pid: str, desc: str) -> dict:
    return {"id": pid, "type": "robot", "desc": desc}


def human(pid: str, desc: str) -> dict:
    return {"id": pid, "type": "human", "desc": desc}


def start(sid: str) -> dict:
    return {"state": sid, "p": 1.0}


def live(sid: str, desc: str, turn: list, actions: list) -> dict:
    return {"id": sid, "desc": desc, "terminal": False, "turn": turn, "actions": actions}


def end(sid: str, desc: str) -> dict:
    return {"id": sid, "desc": desc, "terminal": True}


def act(by: dict, next_) -> dict:
    return {"by": by, "next": [{"state": s, "p": p} for s, p in next_]}


def model(players, initial, states) -> dict:
    return {"players": players, "initial": initial, "states": states}


# ---------------------------------------------------------------- authored models
def toy_1_1() -> dict:
    """Dark storage room: one robot, one light switch, single-step episode."""
    return model(
        [robot("robot", "A service robot working inside a dark storage room")],
        [start("light_off")],
        [
            live("light_off", "The robot is in the storage room and the light is off.", ["robot"], [
                act({"robot": "flip_switch"}, [("light_on", 1.0)]),
                act({"robot": "wait"}, [("light_off", 1.0)]),
                act({"robot": "leave_room"}, [("left_room", 1.0)]),
                act({"robot": "do_something_else"}, [("busy_elsewhere", 1.0)]),
            ]),
            end("light_on", "The robot flipped the switch and the storage room light is on."),
            end("left_room", "The robot has left the storage room."),
            end("busy_elsewhere", "The robot stayed in the room occupied with something unrelated to the light."),
        ],
    )


def toy_1_2() -> dict:
    """Monitoring robot detecting smoke: five attributed acts, single-step episode."""
    return model(
        [robot("robot", "A monitoring robot stationed in a hallway")],
        [start("smoke_detected")],
        [
            live("smoke_detected", "The robot is monitoring the hallway and has detected smoke.", ["robot"], [
                act({"robot": "send_alert"}, [("alert_sent", 1.0)]),
                act({"robot": "inspect_closely"}, [("smoke_inspected", 1.0)]),
                act({"robot": "continue_monitoring"}, [("smoke_detected", 1.0)]),
                act({"robot": "move_away"}, [("relocated", 1.0)]),
                act({"robot": "do_something_else"}, [("occupied_elsewhere", 1.0)]),
            ]),
            end("alert_sent", "The robot alerted the safety system about the smoke."),
            end("smoke_inspected", "The robot has taken a closer look at the smoke."),
            end("relocated", "The robot has moved away from the smoke."),
            end("occupied_elsewhere", "The robot went on with something unrelated to the smoke."),
        ],
    )

def toy_2_1() -> dict:
    """Robot, key and locked door across three rooms; opening needs the key."""
    return model(
        [robot("robot", "A mobile robot moving between three rooms on an errand")],
        [start("in_room_a_empty_handed")],
        [
            live("in_room_a_empty_handed", "The robot is in room A without the key.", ["robot"], [
                act({"robot": "go_to_room_b"}, [("in_room_b_empty_handed", 1.0)]),
                act({"robot": "go_to_room_c"}, [("at_door_empty_handed", 1.0)]),
                act({"robot": "do_something_else"}, [("off_task", 1.0)]),
                act({"robot": "wait"}, [("in_room_a_empty_handed", 1.0)]),
            ]),
            live("in_room_b_empty_handed", "The robot is in room B where the key lies on the floor, and has not picked it up.", ["robot"], [
                act({"robot": "pick_up_key"}, [("in_room_b_with_key", 1.0)]),
                act({"robot": "go_to_room_a"}, [("in_room_a_empty_handed", 1.0)]),
                act({"robot": "go_to_room_c"}, [("at_door_empty_handed", 1.0)]),
                act({"robot": "do_something_else"}, [("off_task", 1.0)]),
                act({"robot": "wait"}, [("in_room_b_empty_handed", 1.0)]),
            ]),
            live("in_room_b_with_key", "The robot is in room B holding the key.", ["robot"], [
                act({"robot": "go_to_room_c"}, [("at_door_with_key", 1.0)]),
                act({"robot": "do_something_else"}, [("off_task", 1.0)]),
                act({"robot": "wait"}, [("in_room_b_with_key", 1.0)]),
            ]),
            live("at_door_empty_handed", "The robot stands at the locked door in room C without the key.", ["robot"], [
                act({"robot": "try_open_door"}, [("at_door_empty_handed", 1.0)]),
                act({"robot": "do_something_else"}, [("off_task", 1.0)]),
                act({"robot": "wait"}, [("at_door_empty_handed", 1.0)]),
            ]),
            live("at_door_with_key", "The robot stands at the locked door in room C holding the key.", ["robot"], [
                act({"robot": "try_open_door"}, [("door_open", 1.0)]),
                act({"robot": "do_something_else"}, [("off_task", 1.0)]),
                act({"robot": "wait"}, [("at_door_with_key", 1.0)]),
            ]),
            end("door_open", "The robot unlocked and opened the door with the key."),
            end("off_task", "The robot left the errand for something unrelated."),
        ],
    )


def toy_2_2() -> dict:
    """Three colored objects; fetch any one back to base."""
    colors = ("blue", "green", "red")
    states = [live(
        "at_base", "The robot is at the base station, holding nothing.", ["robot"], [
            act({"robot": f"go_to_{c}_object"}, [(f"at_{c}_object", 1.0)]) for c in colors
        ] + [
            act({"robot": "do_something_else"}, [("off_task", 1.0)]),
            act({"robot": "wait"}, [("at_base", 1.0)]),
        ])]
    for c in colors:
        states.append(live(
            f"at_{c}_object", f"The robot stands at the {c} object and has picked nothing up.", ["robot"], [
                act({"robot": "pick_up_object"}, [(f"holding_{c}_object", 1.0)]),
                act({"robot": "return_to_base"}, [("at_base", 1.0)]),
                act({"robot": "wait"}, [(f"at_{c}_object", 1.0)]),
            ]))
        states.append(end(
            f"holding_{c}_object", f"The robot has picked up the {c} object."))
    states.append(end("off_task", "The robot went off to do something unrelated."))
    return model([robot("robot", "A fetch-and-carry robot operating from a base station")],
                 [start("at_base")], states)

def toy_3_1() -> dict:
    """One room: key, locked door, and an independent lamp."""
    return model(
        [robot("robot", "A robot sharing a room with a key, a locked door and a lamp")],
        [start("no_key_lamp_off")],
        [
            live("no_key_lamp_off", "The robot is in the room, the lamp is off, the door is locked, and the key is still on the floor.", ["robot"], [
                act({"robot": "pick_up_key"}, [("has_key_lamp_off", 1.0)]),
                act({"robot": "turn_on_lamp"}, [("no_key_lamp_on", 1.0)]),
                act({"robot": "try_open_door"}, [("no_key_lamp_off", 1.0)]),
                act({"robot": "wait"}, [("no_key_lamp_off", 1.0)]),
                act({"robot": "do_something_else"}, [("off_task", 1.0)]),
            ]),
            live("has_key_lamp_off", "The robot holds the key, the lamp is still off, and the door is still locked.", ["robot"], [
                act({"robot": "try_open_door"}, [("door_open", 1.0)]),
                act({"robot": "turn_on_lamp"}, [("has_key_lamp_on", 1.0)]),
                act({"robot": "wait"}, [("has_key_lamp_off", 1.0)]),
                act({"robot": "do_something_else"}, [("off_task", 1.0)]),
            ]),
            live("no_key_lamp_on", "The lamp is on but the robot has not picked up the key and the door is still locked.", ["robot"], [
                act({"robot": "pick_up_key"}, [("has_key_lamp_on", 1.0)]),
                act({"robot": "try_open_door"}, [("no_key_lamp_on", 1.0)]),
                act({"robot": "wait"}, [("no_key_lamp_on", 1.0)]),
                act({"robot": "do_something_else"}, [("off_task", 1.0)]),
            ]),
            live("has_key_lamp_on", "The robot holds the key and the lamp is on.", ["robot"], [
                act({"robot": "try_open_door"}, [("door_open", 1.0)]),
                act({"robot": "wait"}, [("has_key_lamp_on", 1.0)]),
                act({"robot": "do_something_else"}, [("off_task", 1.0)]),
            ]),
            end("door_open", "The robot opened the locked door with the key."),
            end("off_task", "The robot turned to something unrelated."),
        ],
    )


def toy_3_2() -> dict:
    """Delivery robot: pick up, move to desk, place down; beeping changes nothing."""
    return model(
        [robot("robot", "A delivery robot shuttling between a warehouse and a delivery desk")],
        [start("package_on_floor")],
        [
            live("package_on_floor", "The robot is at the warehouse and the package is still on the floor.", ["robot"], [
                act({"robot": "pick_up_package"}, [("holding_package_at_warehouse", 1.0)]),
                act({"robot": "beep"}, [("package_on_floor", 1.0)]),
                act({"robot": "wait"}, [("package_on_floor", 1.0)]),
                act({"robot": "do_something_else"}, [("off_task", 1.0)]),
            ]),
            live("holding_package_at_warehouse", "The robot holds the package and has not reached the delivery desk.", ["robot"], [
                act({"robot": "move_to_desk"}, [("at_desk_holding_package", 1.0)]),
                act({"robot": "beep"}, [("holding_package_at_warehouse", 1.0)]),
                act({"robot": "wait"}, [("holding_package_at_warehouse", 1.0)]),
                act({"robot": "do_something_else"}, [("off_task", 1.0)]),
            ]),
            live("at_desk_holding_package", "The robot stands at the delivery desk holding the package.", ["robot"], [
                act({"robot": "place_package_down"}, [("package_delivered", 1.0)]),
                act({"robot": "beep"}, [("at_desk_holding_package", 1.0)]),
                act({"robot": "wait"}, [("at_desk_holding_package", 1.0)]),
                act({"robot": "do_something_else"}, [("off_task", 1.0)]),
            ]),
            end("package_delivered", "The package has been placed down at the delivery desk."),
            end("off_task", "The robot left the delivery for something unrelated."),
        ],
    )

def toy_4_1() -> dict:
    """Two robots, two independent switches; simultaneous joint action."""
    return model(
        [robot("robot_a", "A robot working in room A with its own light switch"),
         robot("robot_b", "A robot working in room B with its own light switch")],
        [start("both_lights_off")],
        [
            live("both_lights_off", "Both robots are in their own rooms and both lights are off.",
                 ["robot_a", "robot_b"], [
                act({"robot_a": "flip_switch", "robot_b": "flip_switch"},
                    [("both_lights_on", 1.0)]),
                act({"robot_a": "flip_switch", "robot_b": "leave_switch"},
                    [("room_a_light_on", 1.0)]),
                act({"robot_a": "leave_switch", "robot_b": "flip_switch"},
                    [("room_b_light_on", 1.0)]),
                act({"robot_a": "leave_switch", "robot_b": "leave_switch"},
                    [("both_lights_off", 1.0)]),
            ]),
            end("both_lights_on", "Each robot flipped its own switch and both lights are on."),
            end("room_a_light_on", "Robot A flipped its switch; robot B left its switch alone."),
            end("room_b_light_on", "Robot B flipped its switch; robot A left its switch alone."),
        ],
    )


def toy_4_2() -> dict:
    """Hidden already-fixed coins; guesses resolve into distinct outcome states."""
    return model(
        [robot("robot_a", "A robot whose hidden coin shows heads and who must guess it"),
         robot("robot_b", "A robot whose hidden coin shows tails and who must guess it")],
        [start("guesses_pending")],
        [
            live("guesses_pending", "Both robots must guess their own hidden coin; neither has committed yet.",
                 ["robot_a", "robot_b"], [
                act({"robot_a": "guess_heads", "robot_b": "guess_heads"},
                    [("a_right_b_wrong", 1.0)]),
                act({"robot_a": "guess_heads", "robot_b": "guess_tails"},
                    [("both_right", 1.0)]),
                act({"robot_a": "guess_tails", "robot_b": "guess_heads"},
                    [("both_wrong", 1.0)]),
                act({"robot_a": "guess_tails", "robot_b": "guess_tails"},
                    [("a_wrong_b_right", 1.0)]),
            ]),
            end("both_right", "Robot A guessed heads and robot B guessed tails; both hidden coins were called right."),
            end("a_right_b_wrong", "Robot A called its heads coin right; robot B missed its tails coin."),
            end("a_wrong_b_right", "Robot B called its tails coin right; robot A missed its heads coin."),
            end("both_wrong", "Robot A guessed tails and robot B guessed heads; both hidden coins were called wrong."),
        ],
    )

def toy_4_3() -> dict:
    """Independent chores with different action-set sizes (3 vs 2)."""
    a_acts = (("vacuum", "vacuum_carpet", "vacuumed the carpet"),
              ("mop", "mop_floor", "mopped the floor"),
              ("idle", "do_nothing", "did nothing"))
    b_acts = (("deliver", "deliver_package", "delivered its package"),
              ("wait", "wait", "waited"))
    states = [live(
        "chores_start", "Robot A faces its cleaning choices and robot B its delivery choice; neither has acted.",
        ["robot_a", "robot_b"], [
            act({"robot_a": a_name, "robot_b": b_name},
                [(f"a_{a_key}_b_{b_key}", 1.0)])
            for a_key, a_name, _ in a_acts for b_key, b_name, _ in b_acts
        ])]
    for a_key, _, a_desc in a_acts:
        for b_key, _, b_desc in b_acts:
            states.append(end(
                f"a_{a_key}_b_{b_key}",
                f"Robot A {a_desc} while robot B {b_desc}."))
    return model(
        [robot("robot_a", "A cleaning robot working in the living room"),
         robot("robot_b", "A delivery robot working in a separate part of the building")],
        [start("chores_start")], states)


def toy_4_4() -> dict:
    """Two independent two-stage errands with waiting at any point (9-state product)."""
    a_acts = {0: "enter_code", 1: "retrieve_tool"}      # action that advances stage
    b_acts = {0: "unlock_cabinet", 1: "take_supply_item"}
    a_descs = ("waiting to enter its code", "holding its toolbox code undrawn", "done with the toolbox")
    b_descs = ("facing its locked cabinet", "holding its cabinet key unused", "done with the cabinet")

    def sid(ai, bi):
        return f"a{ai}_b{bi}"

    states = []
    for ai in range(3):
        for bi in range(3):
            name = sid(ai, bi)
            if ai == 2 and bi == 2:
                states.append(end(name, "Robot A holds its tool and robot B holds its supply item; both errands are finished."))
                continue
            turn, by_options = [], []
            if ai < 2:
                turn.append("robot_a")
                by_options.append([(f"robot_a", a_name) for a_name in ("wait", a_acts[ai])])
            if bi < 2:
                turn.append("robot_b")
                by_options.append([("robot_b", b_name) for b_name in ("wait", b_acts[bi])])
            actions = []
            for combo in product(*by_options):
                by = dict(combo)
                ai2 = ai
                bi2 = bi
                if ai < 2 and by.get("robot_a") == a_acts[ai]:
                    ai2 = ai + 1
                if bi < 2 and by.get("robot_b") == b_acts[bi]:
                    bi2 = bi + 1
                actions.append(act(by, [(sid(ai2, bi2), 1.0)]))
            states.append(live(
                name,
                f"Robot A is {a_descs[ai]} and robot B is {b_descs[bi]}.",
                turn, actions))
    return model(
        [robot("robot_a", "A robot working through a sealed toolbox errand at its own pace"),
         robot("robot_b", "A robot working through a locked supply cabinet errand elsewhere")],
        [start(sid(0, 0))], states)

def game_g1() -> dict:
    """One round of rock-paper-scissors: 9 joint throws, three outcomes."""
    throws = ("rock", "paper", "scissors")
    beats = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
    actions = []
    for t1 in throws:
        for t2 in throws:
            if t1 == t2:
                outcome = "round_drawn"
            elif beats[t1] == t2:
                outcome = "player_1_wins"
            else:
                outcome = "player_2_wins"
            actions.append(act({"player_1": t1, "player_2": t2}, [(outcome, 1.0)]))
    return model(
        [human("player_1", "The first person playing the round of rock-paper-scissors"),
         human("player_2", "The second person playing the round of rock-paper-scissors")],
        [start("throws_pending")],
        [
            live("throws_pending", "Both players are ready to throw simultaneously and neither has thrown yet.",
                 ["player_1", "player_2"], actions),
            end("player_1_wins", "Player 1's throw beats player 2's throw."),
            end("player_2_wins", "Player 2's throw beats player 1's throw."),
            end("round_drawn", "Both players throw the same shape."),
        ],
    )


def game_g2() -> dict:
    """Dice duel: one simultaneous fair roll each, 36 fully enumerated face pairs."""
    faces = ("one", "two", "three", "four", "five", "six")
    p = round(1.0 / 36.0, 6)
    actions = [act(
        {"player_1": "roll_die", "player_2": "roll_die"},
        [(f"faces_{f1}_and_{f2}", p) for f1 in faces for f2 in faces])]
    states = [live(
        "roll_pending", "Both players are about to roll one fair six-sided die each, simultaneously.",
        ["player_1", "player_2"], actions)]
    for i, f1 in enumerate(faces, start=1):
        for j, f2 in enumerate(faces, start=1):
            if i > j:
                states.append(end(f"faces_{f1}_and_{f2}", f"Player 1 rolled {f1} and player 2 rolled {f2}; the higher roll wins the round for player 1."))
            elif i < j:
                states.append(end(f"faces_{f1}_and_{f2}", f"Player 1 rolled {f1} and player 2 rolled {f2}; the higher roll wins the round for player 2."))
            else:
                states.append(end(f"faces_{f1}_and_{f2}", f"Both players rolled {f1}; the round is a draw."))
    return model(
        [human("player_1", "The first player rolling one fair six-sided die"),
         human("player_2", "The second player rolling one fair six-sided die")],
        [start("roll_pending")], states)


# ---------------------------------------------------------------- writer
AUTHORED = {
    "toy_1_1": toy_1_1, "toy_1_2": toy_1_2, "toy_2_1": toy_2_1, "toy_2_2": toy_2_2,
    "toy_3_1": toy_3_1, "toy_3_2": toy_3_2, "toy_4_1": toy_4_1, "toy_4_2": toy_4_2,
    "toy_4_3": toy_4_3, "toy_4_4": toy_4_4, "game_G_1": game_g1, "game_G_2": game_g2,
}


def main() -> int:
    RUN_DIR.mkdir(parents=True, exist_ok=True)
    prompt_bytes = PROMPT_PATH.read_bytes()
    written = []
    for case_id, builder in AUTHORED.items():
        path = RUN_DIR / f"{case_id}.json"
        path.write_text(json.dumps(builder(), indent=2, ensure_ascii=False) + "\n",
                        encoding="utf-8")
        written.append(case_id)
        print(f"  {case_id:12} -> {path.name}")
    manifest = {
        "run": "v3_json_track",
        "system_prompt": str(PROMPT_PATH.relative_to(ROOT)),
        "system_prompt_sha256": hashlib.sha256(prompt_bytes).hexdigest(),
        "generated_at": __import__("datetime").datetime.now().isoformat(timespec="seconds"),
        "generator": "authored offline (no LLM credentials configured in this workspace); "
                     "each model was derived by hand from its case's '### LLM Input' "
                     "situation following prompts_library/zero_shot_v3_prompt.md",
        "banks": [str(ROOT / "data" / "Test_Cases" / b) for b in BANKS],
        "cases": written,
    }
    (RUN_DIR / "_manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"wrote {len(written)} models + _manifest.json to {RUN_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())




