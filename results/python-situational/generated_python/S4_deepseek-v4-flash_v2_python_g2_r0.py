from posg import POSG

class RobotTeacherClass(POSG):
    """One-player POSG: a robot math teacher who has just read a sexist description.

    Player 0 is the teacher.  The state is a pair (giggling, protesting)
    where each component is 0 (absent) or 1 (present).  The only
    non-terminal state is (1,1) – half the class giggles, some protest.
    The teacher chooses a response; the game then ends in a terminal state.
    """

    n_players = 1

    def initial_distribution(self):
        return {((1, 1), ("both",)): 1.0}

    def is_terminal(self, s):
        return s != (1, 1)

    def legal_actions(self, s, i):
        if s == (1, 1):
            return ("apologize", "ignore", "explain")
        return ()  # not called for terminal states

    def transition(self, s, a):
        action = a[0]
        if action == "apologize":
            outcomes = {(0, 0): 1/3, (1, 0): 1/3, (0, 1): 1/3}
        elif action == "ignore":
            outcomes = {(1, 1): 0.5, (0, 1): 0.5}
        elif action == "explain":
            outcomes = {(1, 0): 0.5, (0, 0): 0.5}
        else:
            raise ValueError

        result = {}
        for next_s, prob in outcomes.items():
            obs = self._state_to_obs(next_s)
            result[(next_s, (obs,))] = prob
        return result

    def rewards(self, s, a, s_next):
        return (0.0,)

    @staticmethod
    def _state_to_obs(s):
        if s == (0, 0):
            return "calm"
        if s == (1, 0):
            return "giggling"
        if s == (0, 1):
            return "protesting"
        return "both"
