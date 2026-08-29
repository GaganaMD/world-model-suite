class GeneratedPOSG(AbstractPOSG):
    """
    Two-round Stag Hunt with imperfect monitoring and weather chance.

    Round 1: both hunters simultaneously choose "stag" or "hare".
      - Terrain/weather chance determines whether a joint stag hunt succeeds
        (success prob 0.8) or fails (0.2, stag escapes).
      - Each hunter observes only a noisy signal about the partner's choice
        in round 1 (signal correct with prob 0.8).
    Round 2: choose again, with the same payoff structure (no noise needed
      afterwards since the game ends).

    States (strings):
      "start"
      "r2|<a1>|<a2>|<res>"   history after round 1 (res in {stag,none,hare})
      "terminal"
    """

    STAG_SUCCESS = 0.8
    SIGNAL_CORRECT = 0.8

    # ---- interface ----

    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "start"

    def legal_actions(self, state, player):
        return ["stag", "hare"]

    def transition(self, state, joint_action):
        a1 = joint_action["player_1"]
        a2 = joint_action["player_2"]

        if state == "start":
            if a1 == "stag" and a2 == "stag":
                p = self.STAG_SUCCESS
                return {
                    "r2|stag|stag|stag": p,
                    "r2|stag|stag|none": 1.0 - p,
                }
            # no joint stag hunt: outcome is deterministic
            return {"r2|" + a1 + "|" + a2 + "|hare": 1.0}

        # any round-2 state ends the game
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        a1 = joint_action["player_1"]
        a2 = joint_action["player_2"]
        own = a1 if player == "player_1" else a2
        other = a2 if player == "player_1" else a1

        if state == "start":
            parts = next_state.split("|")
            res = parts[3] if len(parts) == 4 else "none"
            # noisy signal about partner's action encoded in state-independent way:
            # deterministic decoding is impossible here, so report the true
            # partner action only when the stag result reveals it.
            if own == "stag" and res == "stag":
                signal = "stag"
            elif own == "stag" and res == "none":
                signal = "unclear"
            else:
                signal = "unclear"
            return f"round=1;own={own};result={res};partner_signal={signal}"

        # round 2 -> terminal
        joint = "stag" if (a1 == "stag" and a2 == "stag") else "no"
        return f"round=2;own={own};partner={other};joint_stag={joint}"

    def reward(self, state, joint_action, next_state, player):
        a1 = joint_action["player_1"]
        a2 = joint_action["player_2"]
        own = a1 if player == "player_1" else a2
        other = a2 if player == "player_1" else a1

        if state == "start":
            parts = next_state.split("|")
            res = parts[3] if len(parts) == 4 else "none"
            if own == "hare":
                return 1.0
            # own == "stag"
            if other == "stag" and res == "stag":
                return 4.0
            return 0.0

        if state == "terminal":
            return 0.0

        # round 2 decision: resolve deterministically
        if own == "hare":
            return 1.0
        if other == "stag":
            return 4.0 * self.STAG_SUCCESS
        return 0.0

    def is_terminal(self, state):
        return state == "terminal"
