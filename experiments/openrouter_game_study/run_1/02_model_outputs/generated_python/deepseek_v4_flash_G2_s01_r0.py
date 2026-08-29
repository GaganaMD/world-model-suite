class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "roll"

    def legal_actions(self, state, player):
        if state == "roll":
            return ["roll"]
        elif state.startswith("p1_") and state.endswith("_p2_turn"):
            # After p1 rolls, p2 chooses to see or not (but no strategic choice here; we just proceed)
            return ["proceed"]
        elif state.startswith("p1_") and state.endswith("_p2_rolled"):
            # After both rolled, no actions; but we need non-empty for non-terminal? Actually terminal handled separately.
            return ["none"]
        else:
            return ["none"]

    def transition(self, state, joint_action):
        if state == "roll":
            # Both players roll simultaneously. We model as chance: each outcome equally likely.
            # We'll create 36 possible next states, each with prob 1/36.
            # State format: "p1_<die1>_p2_<die2>_p2_turn" after roll, then p2 "proceed" leads to terminal.
            # But to keep it simple, we directly go to a state where both dice are known and then terminal.
            # We'll use a single state "p1_<d1>_p2_<d2>_p2_turn" and then p2 action "proceed" -> terminal.
            # However, we need to handle the fact that after roll, p2 has an action. But the game is simultaneous, so we can just go to terminal directly.
            # To satisfy the interface, we'll have a state "roll" -> "p1_<d1>_p2_<d2>_p2_turn" with prob 1/36.
            # Then from that state, p2 action "proceed" -> terminal with prob 1.
            # But we need to define legal_actions for that state. We'll do that.
            # For simplicity, we'll generate all 36 outcomes.
            outcomes = {}
            for d1 in range(1,7):
                for d2 in range(1,7):
                    next_state = f"p1_{d1}_p2_{d2}_p2_turn"
                    outcomes[next_state] = outcomes.get(next_state, 0) + 1/36
            return outcomes
        elif state.startswith("p1_") and state.endswith("_p2_turn"):
            # p2 action "proceed" -> terminal
            return {"terminal": 1.0}
        else:
            return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        # In this simultaneous game, each player only knows their own die? But the problem says "whoever rolls higher wins", but no hidden info specified.
        # Since it's a simple dice roll, we can give full observation of the state (both dice) to both players.
        # But to be safe, we give each player their own die and the fact that the round is over.
        if state == "roll":
            # Before rolling, no observation.
            return "start"
        elif state.startswith("p1_") and state.endswith("_p2_turn"):
            # After roll, both know the outcome.
            # Extract dice from state.
            parts = state.split("_")
            d1 = parts[1]
            d2 = parts[3]
            if player == "player_1":
                return f"p1_die_{d1}_p2_die_{d2}"
            else:
                return f"p1_die_{d1}_p2_die_{d2}"
        else:
            return "terminal_obs"

    def reward(self, state, joint_action, next_state, player):
        # Reward based on who wins.
        if state.startswith("p1_") and state.endswith("_p2_turn"):
            parts = state.split("_")
            d1 = int(parts[1])
            d2 = int(parts[3])
            if d1 > d2:
                return 1.0 if player == "player_1" else -1.0
            elif d2 > d1:
                return 1.0 if player == "player_2" else -1.0
            else:
                return 0.0
        else:
            return 0.0

    def is_terminal(self, state):
        return state == "terminal"
