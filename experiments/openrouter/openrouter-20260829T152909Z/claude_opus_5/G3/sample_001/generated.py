class GeneratedPOSG(AbstractPOSG):
    """Two players simultaneously call 'heads' or 'tails'; a fair coin is then flipped.

    States:
        "s0"                                    -- initial, calls not yet made
        ("done", call_1, call_2, coin_result)   -- terminal outcome state
    """

    CALLS = ("heads", "tails")

    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        return ["heads", "tails"]

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        a1 = joint_action.get("player_1", "heads")
        a2 = joint_action.get("player_2", "heads")
        if a1 not in self.CALLS:
            a1 = "heads"
        if a2 not in self.CALLS:
            a2 = "heads"

        return {
            ("done", a1, a2, "heads"): 0.5,
            ("done", a1, a2, "tails"): 0.5,
        }

    def observation(self, state, joint_action, next_state, player):
        if not (isinstance(next_state, tuple) and len(next_state) == 4):
            return "waiting_for_flip"

        _, a1, a2, coin = next_state
        own_call = a1 if player == "player_1" else a2
        opp_call = a2 if player == "player_1" else a1
        result = self._result_for(player, next_state)
        return ("flip_result", coin, "my_call", own_call, "opponent_call", opp_call, result)

    def reward(self, state, joint_action, next_state, player):
        if not (isinstance(next_state, tuple) and len(next_state) == 4):
            return 0.0
        result = self._result_for(player, next_state)
        if result == "win":
            return 1.0
        if result == "loss":
            return -1.0
        return 0.0

    def is_terminal(self, state):
        return isinstance(state, tuple) and len(state) == 4 and state[0] == "done"

    def _result_for(self, player, terminal_state):
        _, a1, a2, coin = terminal_state
        correct_1 = (a1 == coin)
        correct_2 = (a2 == coin)
        if correct_1 == correct_2:
            return "draw"
        winner_is_1 = correct_1
        if (player == "player_1") == winner_is_1:
            return "win"
        return "loss"