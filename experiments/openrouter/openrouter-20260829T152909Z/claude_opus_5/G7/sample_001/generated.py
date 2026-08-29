class GeneratedPOSG(AbstractPOSG):
    """Classic one-shot Prisoner's Dilemma as a POSG.

    States:
        "interrogation"                  -> initial, non-terminal decision state
        ("outcome", a1, a2)              -> terminal state recording both choices

    Actions:
        "silent"    -> stay silent (cooperate with the other suspect)
        "testify"   -> testify against the other suspect (defect)
    """

    SILENT = "silent"
    TESTIFY = "testify"

    # Sentences in years (negative reward = time served).
    LIGHT = 1.0     # both silent
    HEAVY = 5.0     # both testify
    MAXIMUM = 10.0  # silent while the other testifies
    FREE = 0.0      # testified while the other stayed silent

    @property
    def players(self):
        return ["player_1", "player_2"]

    def initial_state(self):
        return "interrogation"

    def legal_actions(self, state, player):
        if self.is_terminal(state):
            return []
        return [self.SILENT, self.TESTIFY]

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}

        a1 = joint_action.get("player_1", self.SILENT)
        a2 = joint_action.get("player_2", self.SILENT)

        if a1 not in (self.SILENT, self.TESTIFY):
            a1 = self.SILENT
        if a2 not in (self.SILENT, self.TESTIFY):
            a2 = self.SILENT

        return {("outcome", a1, a2): 1.0}

    def observation(self, state, joint_action, next_state, player):
        # During interrogation each suspect only learns their own choice;
        # once the outcome is reached, the court proceedings reveal both choices.
        if isinstance(next_state, tuple) and next_state[0] == "outcome":
            own = joint_action.get(player, self.SILENT)
            if player == "player_1":
                other = joint_action.get("player_2", self.SILENT)
            else:
                other = joint_action.get("player_1", self.SILENT)
            return ("verdict", own, other)
        return ("waiting", joint_action.get(player, self.SILENT))

    def reward(self, state, joint_action, next_state, player):
        if not (isinstance(next_state, tuple) and next_state[0] == "outcome"):
            return 0.0

        a1 = next_state[1]
        a2 = next_state[2]

        if player == "player_1":
            own, other = a1, a2
        elif player == "player_2":
            own, other = a2, a1
        else:
            return 0.0

        if own == self.SILENT and other == self.SILENT:
            return -self.LIGHT
        if own == self.TESTIFY and other == self.TESTIFY:
            return -self.HEAVY
        if own == self.TESTIFY and other == self.SILENT:
            return -self.FREE
        return -self.MAXIMUM

    def is_terminal(self, state):
        return isinstance(state, tuple) and len(state) == 3 and state[0] == "outcome"