class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self): return ["commander_1", "commander_2"]
    def initial_state(self): return ("0-3", "0-3")
    def legal_actions(self, state, player):
        battlefield = int(state[player].split('-')[0])
        soldiers = int(state[player].split('-')[1])
        actions = []
        for i in range(soldiers + 1):
            actions.append(f"{i}-{soldiers-i}")
        return actions
    def transition(self, state, joint_action):
        next_state = (joint_action["commander_1"], joint_action["commander_2"])
        if self.is_terminal(next_state):
            return {"terminal": 1.0}
        else:
            return {next_state: 1.0}
    def observation(self, state, joint_action, next_state, player):
        battlefield = int(state[player].split('-')[0])
        soldiers = int(state[player].split('-')[1])
        action_taken = joint_action[player]
        if action_taken == f"{soldiers}-{soldiers-soldiers}":
            return "no_change"
        elif action_taken == f"0-{soldiers}":
            return "all_to_one"
        else:
            return "partial_to_one"
    def reward(self, state, joint_action, next_state, player):
        battlefield = int(state[player].split('-')[0])
        soldiers = int(state[player].split('-')[1])
        action_taken = joint_action[player]
        if self.is_terminal(next_state):
            commander_1_wins = int(next_state[0].split('-')[0]) > int(next_state[1].split('-')[0])
            commander_2_wins = int(next_state[1].split('-')[0]) > int(next_state[0].split('-')[0])
            if player == "commander_1":
                return 1.0 if commander_1_wins else -1.0
            elif player == "commander_2":
                return 1.0 if commander_2_wins else -1.0
        else:
            return 0.0
    def is_terminal(self, state):
        battlefield_1 = int(state[0].split('-')[0])
        battlefield_2 = int(state[1].split('-')[0])
        return battlefield_1 == 3 or battlefield_2 == 3