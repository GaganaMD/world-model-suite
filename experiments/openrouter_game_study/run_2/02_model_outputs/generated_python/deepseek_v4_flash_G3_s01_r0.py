class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if state == "s0":
            return ["heads", "tails"]
        # terminal state has no actions
        return []

    def transition(self, state, joint_action):
        if state == "s0":
            # joint_action is dict with keys "player_1", "player_2"
            p1 = joint_action["player_1"]
            p2 = joint_action["player_2"]
            # coin flip: heads or tails with equal probability
            return {
                "s1_heads": 0.5,
                "s1_tails": 0.5
            }
        # terminal states have no transitions
        return {"terminal": 1.0}

    def observation(self, state, joint_action, next_state, player):
        if state == "s0":
            # before the coin flip, players observe nothing (or their own action? but we keep simple)
            # we return a string indicating the state and player
            return f"state_{state}_player_{player}"
        # after the flip, next_state encodes the coin result
        if next_state == "s1_heads":
            return f"coin_heads_player_{player}"
        elif next_state == "s1_tails":
            return f"coin_tails_player_{player}"
        # terminal
        return "terminal_obs"

    def reward(self, state, joint_action, next_state, player):
        if state == "s0":
            # no reward until after the flip
            return 0.0
        # after the flip, determine outcome
        # need to know the actions chosen in s0, but we don't have them here.
        # We'll encode the outcome in the next_state and use a deterministic reward based on player and coin.
        # But we need to know the actions. Since we don't have them, we'll compute from the joint_action? 
        # However, reward is called with state, joint_action, next_state, player.
        # In s0, joint_action contains the choices. In s1_* states, joint_action is not used.
        # We'll handle by checking if state is s0: return 0.
        # For s1_* states, we need to know the actions. But we don't have them.
        # To satisfy the contract, we can compute reward based on next_state and player only, but that would be incorrect.
        # Instead, we can design the reward to be given only at the transition from s0 to s1_*.
        # So we'll compute reward in the transition from s0.
        # But the interface requires reward(state, joint_action, next_state, player).
        # We'll compute based on the joint_action and next_state.
        if state == "s0":
            p1 = joint_action["player_1"]
            p2 = joint_action["player_2"]
            coin = "heads" if next_state == "s1_heads" else "tails"
            # Determine winner
            if p1 == coin and p2 == coin:
                # both match -> draw
                return 0.0
            elif p1 == coin and p2 != coin:
                # p1 wins
                return 1.0 if player == "player_1" else -1.0
            elif p1 != coin and p2 == coin:
                # p2 wins
                return -1.0 if player == "player_1" else 1.0
            else:
                # neither matches -> draw
                return 0.0
        # terminal states have no reward
        return 0.0

    def is_terminal(self, state):
        return state == "terminal"
