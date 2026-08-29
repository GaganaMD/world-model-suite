BID_LEVELS = ("0", "2", "4", "6")
VALUE_TABLE = {"low": 3.0, "high": 7.0}


class GeneratedPOSG(AbstractPOSG):
    """Two-player sealed-bid first-price auction with private (low/high) values.

    State layout (all hashable tuples / strings):
      "s0"                                  -> chance root, values not yet drawn
      ("values", v1, v2)                    -> private values drawn, bids pending
      ("end", v1, v2, b1, b2, winner)       -> terminal, winner in {"player_1",
                                              "player_2"}
    """

    # ------------------------------------------------------------------ setup
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    # ---------------------------------------------------------------- actions
    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        if state == "s0":
            # Nature draws the private values; agents merely wait.
            return ["wait"]
        if isinstance(state, tuple) and state[0] == "values":
            return list(BID_LEVELS)
        return ["wait"]

    # ------------------------------------------------------------ transitions
    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        if state == "s0":
            # Independent private values, each low/high with prob 1/2.
            return {
                ("values", "low", "low"): 0.25,
                ("values", "low", "high"): 0.25,
                ("values", "high", "low"): 0.25,
                ("values", "high", "high"): 0.25,
            }

        if isinstance(state, tuple) and state[0] == "values":
            v1 = state[1]
            v2 = state[2]
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            b1 = a1 if a1 in BID_LEVELS else "0"
            b2 = a2 if a2 in BID_LEVELS else "0"
            n1 = float(b1)
            n2 = float(b2)
            if n1 > n2:
                return {("end", v1, v2, b1, b2, "player_1"): 1.0}
            if n2 > n1:
                return {("end", v1, v2, b1, b2, "player_2"): 1.0}
            # Tie -> fair coin flip.
            return {
                ("end", v1, v2, b1, b2, "player_1"): 0.5,
                ("end", v1, v2, b1, b2, "player_2"): 0.5,
            }

        # Defensive fallback: never reached with well-formed states.
        return {("end", "low", "low", "0", "0", "player_1"): 1.0}

    # ----------------------------------------------------------- observations
    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            # Each bidder privately learns only its own valuation.
            own = next_state[1] if player == "player_1" else next_state[2]
            return ("private_value", own)

        if isinstance(state, tuple) and state[0] == "values":
            own = state[1] if player == "player_1" else state[2]
            b1 = next_state[3]
            b2 = next_state[4]
            winner = next_state[5]
            own_bid = b1 if player == "player_1" else b2
            rival_bid = b2 if player == "player_1" else b1
            return (
                "auction_result",
                own,
                own_bid,
                rival_bid,
                "won" if winner == player else "lost",
            )

        return ("nothing",)

    # --------------------------------------------------------------- rewards
    def reward(self, state, joint_action, next_state, player):
        if state == "s0":
            return 0.0
        if isinstance(state, tuple) and state[0] == "values":
            winner = next_state[5]
            if winner != player:
                return 0.0
            own_value_label = next_state[1] if player == "player_1" else next_state[2]
            own_bid = next_state[3] if player == "player_1" else next_state[4]
            return VALUE_TABLE[own_value_label] - float(own_bid)
        return 0.0

    # -------------------------------------------------------------- terminal
    def is_terminal(self, state):
        return isinstance(state, tuple) and len(state) > 0 and state[0] == "end"