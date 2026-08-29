class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "s0"

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        if player in ("player_1", "player_2"):
            return [
                "deploy_0_3",
                "deploy_1_2",
                "deploy_2_1",
                "deploy_3_0",
            ]
        return []

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        allocations = {
            "deploy_0_3": (0, 3),
            "deploy_1_2": (1, 2),
            "deploy_2_1": (2, 1),
            "deploy_3_0": (3, 0),
        }
        action_1 = joint_action["player_1"]
        action_2 = joint_action["player_2"]
        allocation_1 = allocations[action_1]
        allocation_2 = allocations[action_2]

        if allocation_1[0] > allocation_2[0]:
            battlefield_1 = "player_1"
        elif allocation_2[0] > allocation_1[0]:
            battlefield_1 = "player_2"
        else:
            battlefield_1 = "tie"

        if allocation_1[1] > allocation_2[1]:
            battlefield_2 = "player_1"
        elif allocation_2[1] > allocation_1[1]:
            battlefield_2 = "player_2"
        else:
            battlefield_2 = "tie"

        player_1_wins = (
            int(battlefield_1 == "player_1")
            + int(battlefield_2 == "player_1")
        )
        player_2_wins = (
            int(battlefield_1 == "player_2")
            + int(battlefield_2 == "player_2")
        )

        if player_1_wins > player_2_wins:
            overall_winner = "player_1"
        elif player_2_wins > player_1_wins:
            overall_winner = "player_2"
        else:
            overall_winner = "draw"

        next_state = (
            "terminal",
            action_1,
            action_2,
            battlefield_1,
            battlefield_2,
            overall_winner,
        )
        return {next_state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        if not self.is_terminal(next_state):
            return "awaiting_deployment"

        if player == "player_1":
            own_action = joint_action["player_1"]
            opponent_action = joint_action["player_2"]
        else:
            own_action = joint_action["player_2"]
            opponent_action = joint_action["player_1"]

        return (
            "own={};opponent={};battlefield_1={};battlefield_2={};overall={}"
            .format(
                own_action,
                opponent_action,
                next_state[3],
                next_state[4],
                next_state[5],
            )
        )

    def reward(self, state, joint_action, next_state, player):
        if not self.is_terminal(next_state):
            return 0.0
        if next_state[5] == "draw":
            return 0.0
        if next_state[5] == player:
            return 1.0
        return -1.0

    def is_terminal(self, state):
        return (
            isinstance(state, tuple)
            and len(state) == 6
            and state[0] == "terminal"
        )