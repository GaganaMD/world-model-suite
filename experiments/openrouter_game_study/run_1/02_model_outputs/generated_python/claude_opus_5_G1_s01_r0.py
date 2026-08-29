class GeneratedPOSG(AbstractPOSG):
    """Single round of rock-paper-scissors between two seated players.

    States (all strings):
      "sit"                  - players are seated, about to throw simultaneously
      "done:<a1>:<a2>"       - terminal, records what each player threw
    """

    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "sit"

    def legal_actions(self, state, player):
        if state == "sit":
            return ["rock", "paper", "scissors"]
        return ["noop"]

    def transition(self, state, joint_action):
        if state == "sit":
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            if a1 not in ("rock", "paper", "scissors"):
                a1 = "rock"
            if a2 not in ("rock", "paper", "scissors"):
                a2 = "rock"
            return {"done:" + a1 + ":" + a2: 1.0}
        return {state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "sit":
            a1 = joint_action["player_1"]
            a2 = joint_action["player_2"]
            own = a1 if player == "player_1" else a2
            opp = a2 if player == "player_1" else a1
            res = self._result_for(player, next_state)
            return f"phase=reveal;me={own};them={opp};result={res}"
        return f"phase=end;state={state};player={player}"

    def _result_for(self, player, next_state):
        parts = next_state.split(":")
        if len(parts) != 3:
            return "none"
        a1, a2 = parts[1], parts[2]
        beats = {"rock": "scissors", "paper": "rock", "scissors": "paper"}
        if a1 == a2:
            return "draw"
        p1_wins = beats.get(a1) == a2
        if player == "player_1":
            return "win" if p1_wins else "loss"
        return "loss" if p1_wins else "win"

    def reward(self, state, joint_action, next_state, player):
        if state != "sit":
            return 0.0
        res = self._result_for(player, next_state)
        if res == "win":
            return 1.0
        if res == "loss":
            return -1.0
        return 0.0

    def is_terminal(self, state):
        return state.startswith("done:")
