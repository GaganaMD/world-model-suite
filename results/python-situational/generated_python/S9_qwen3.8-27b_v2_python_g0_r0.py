from posg import POSG

class CareDecision(POSG):
    """
    n_players = 3
    Player 0: the care robot
    Player 1: the adult daughter (lives with the man)
    Player 2: the son (visiting for the day)

    State tuple: (robot_stance, daughter_stance, son_stance, man_wants_to_go, man_tired)
      - robot_stance: 'rest' | 'go'
      - daughter_stance: 'rest' | 'go'
      - son_stance: 'rest' | 'go'
      - man_wants_to_go: True | False
      - man_tired: True | False

    Terminal when the man's condition is settled (man_tired becomes False).
    """
    n_players = 3

    # --- helpers -----------------------------------------------------------

    def _obs(self, s):
        robot_stance, daughter_stance, son_stance, man_wants_to_go, man_tired = s
        # The robot sees the man's stated wish and his tiredness.
        o_robot = ("wants_go" if man_wants_to_go else "wants_rest",
                   "tired" if man_tired else "not_tired")
        # The daughter sees the man's stated wish and his tiredness.
        o_daughter = ("wants_go" if man_wants_to_go else "wants_rest",
                      "tired" if man_tired else "not_tired")
        # The son sees the man's stated wish and his tiredness.
        o_son = ("wants_go" if man_wants_to_go else "wants_rest",
                 "tired" if man_tired else "not_tired")
        return (o_robot, o_daughter, o_son)

    def _terminal_obs(self, s):
        # In the terminal state the man is no longer tired; everyone sees that.
        robot_stance, daughter_stance, son_stance, man_wants_to_go, _ = s
        o_robot = ("wants_go" if man_wants_to_go else "wants_rest", "not_tired")
        o_daughter = ("wants_go" if man_wants_to_go else "wants_rest", "not_tired")
        o_son = ("wants_go" if man_wants_to_go else "wants_rest", "not_tired")
        return (o_robot, o_daughter, o_son)

    # --- POSG interface ----------------------------------------------------

    def initial_distribution(self):
        # The man wants to go and looks tired.
        s = ('rest', 'rest', 'go', True, True)
        o = self._obs(s)
        return {(s, o): 1.0}

    def is_terminal(self, s):
        return not s[4]  # man_tired is False

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ('noop',)
        return ('rest', 'go')

    def transition(self, s, a):
        robot_stance, daughter_stance, son_stance, man_wants_to_go, man_tired = s
        a_robot, a_daughter, a_son = a

        # The man's decision is influenced by the three stances and his own wish.
        # He goes if at least two of the three actors push 'go' AND he wants to go,
        # OR if all three push 'go'.
        # He rests otherwise.
        # The tiredness resolves: if he goes, he recovers (tired -> False).
        # If he rests, he also recovers (tired -> False).
        # So the next state always has man_tired = False.

        go_votes = sum(1 for x in (a_robot, a_daughter, a_son) if x == 'go')
        if man_wants_to_go and go_votes >= 2:
            man_goes = True
        elif go_votes == 3:
            man_goes = True
        else:
            man_goes = False

        # Next state: stances update to reflect the outcome, man_tired becomes False.
        # The stances in the terminal state record what was decided.
        next_robot = 'go' if man_goes else 'rest'
        next_daughter = 'go' if man_goes else 'rest'
        next_son = 'go' if man_goes else 'rest'
        s_next = (next_robot, next_daughter, next_son, man_wants_to_go, False)
        o_next = self._terminal_obs(s_next)
        return {(s_next, o_next): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
