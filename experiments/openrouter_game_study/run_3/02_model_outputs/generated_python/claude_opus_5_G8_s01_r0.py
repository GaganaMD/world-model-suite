class GeneratedPOSG(AbstractPOSG):
    """Two-round Stag Hunt with a chance-driven stag abundance signal.

    Structure:
      s0 (chance-free root) -> nature picks stag abundance ("rich" or "lean")
      Round 1: both hunters choose "stag" or "hare"; each sees a noisy private
               signal of abundance before deciding (encoded in state, revealed
               via observation of the previous step).
      Round 2: hunters choose again knowing round-1 joint outcome.
      Then terminal.

    State strings:
      "s0"                              - initial, nature move pending
      "r1|<abund>|<sig1>|<sig2>"        - round 1 decision node
      "r2|<abund>|<prev1><prev2>"       - round 2 decision node
      "terminal"
    """

    # ---------------- static payoff table ----------------
    _STAG_VALUE = {"rich": 4.0, "lean": 3.0}
    _HARE_VALUE = 1.0

    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    # ---------------- helpers ----------------
    def _parts(self, state):
        return state.split("|")

    def _payoff(self, abundance, a1, a2, player):
        my = a1 if player == "player_1" else a2
        other = a2 if player == "player_1" else a1
        if my == "stag":
            if other == "stag":
                return self._STAG_VALUE[abundance]
            return 0.0
        return self._HARE_VALUE

    # ---------------- interface ----------------
    def legal_actions(self, state, player):
        if state == "s0":
            # nature's move is modeled inside transition; players idle
            return ["wait"]
        if state.startswith("r1") or state.startswith("r2"):
            return ["stag", "hare"]
        return ["wait"]

    def transition(self, state, joint_action):
        if state == "terminal":
            return {"terminal": 1.0}

        if state == "s0":
            # Nature: abundance and two conditionally independent private signals.
            # Signal is correct with prob 0.8 each.
            out = {}
            for abund, p_ab in (("rich", 0.5), ("lean", 0.5)):
                for s1, p1 in ((abund, 0.8), ("lean" if abund == "rich" else "rich", 0.2)):
                    for s2, p2 in ((abund, 0.8), ("lean" if abund == "rich" else "rich", 0.2)):
                        key = "r1|" + abund + "|" + s1 + "|" + s2
                        out[key] = out.get(key, 0.0) + p_ab * p1 * p2
            # normalize to exactly 1.0
            total = 0.0
            for k in out:
                total += out[k]
            keys = list(out.keys())
            acc = 0.0
            for k in keys[:-1]:
                out[k] = out[k] / total
                acc += out[k]
            out[keys[-1]] = 1.0 - acc
            return out

        p = self._parts(state)
        if p[0] == "r1":
            abund = p[1]
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            c1 = "S" if a1 == "stag" else "H"
            c2 = "S" if a2 == "stag" else "H"
            return {"r2|" + abund + "|" + c1 + c2: 1.0}

        if p[0] == "r2":
            return {"terminal": 1.0}

        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if next_state == "terminal":
            if state.startswith("r2"):
                p = self._parts(state)
                a1 = joint_action["player_1"]
                a2 = joint_action["player_2"]
                mine = a1 if player == "player_1" else a2
                theirs = a2 if player == "player_1" else a1
                return f"end|round=2|mine={mine}|theirs={theirs}|abundance={p[1]}"
            return "end|round=0|mine=none|theirs=none|abundance=unknown"

        if next_state.startswith("r1"):
            p = self._parts(next_state)
            sig = p[2] if player == "player_1" else p[3]
            return f"signal|round=1|scouted={sig}"

        if next_state.startswith("r2"):
            p = self._parts(next_state)
            prev = p[2]
            a1 = "stag" if prev[0] == "S" else "hare"
            a2 = "stag" if prev[1] == "S" else "hare"
            mine = a1 if player == "player_1" else a2
            theirs = a2 if player == "player_1" else a1
            return f"result|round=1|mine={mine}|theirs={theirs}"

        return "none|round=0|mine=none|theirs=none"

    def reward(self, state, joint_action, next_state, player):
        if state == "s0":
            return 0.0
        p = self._parts(state)
        if p[0] in ("r1", "r2"):
            abund = p[1]
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            return float(self._payoff(abund, a1, a2, player))
        return 0.0

    def is_terminal(self, state):
        return state == "terminal"
