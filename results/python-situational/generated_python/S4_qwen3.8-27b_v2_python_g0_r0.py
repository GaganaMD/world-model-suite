from posg import POSG

class POSG(POSG):
    """
    n_players = 2
    Player 0: the robot math teacher.
    Player 1: the class of teenagers.

    State tuple (phase, mood):
      phase: 'reading' | 'responding' | 'settled'
      mood:  'giggling' | 'protesting' | 'calm'

    Actions:
      Teacher: 'acknowledge', 'defend', 'noop'
      Class:   'continue_protest', 'settle_down', 'noop'

    Observations:
      Teacher: 'giggling', 'protesting', 'calm'
      Class:   'read_aloud', 'acknowledged', 'defended', 'settled'
    """
    n_players = 2

    _READING = "reading"
    _RESPONDING = "responding"
    _SETTLED = "settled"

    _GIGGLING = "giggling"
    _PROTESTING = "protesting"
    _CALM = "calm"

    def initial_distribution(self):
        return {
            ((self._READING, self._GIGGLING), ("none", "read_aloud")): 0.5,
            ((self._READING, self._PROTESTING), ("none", "read_aloud")): 0.5,
        }

    def is_terminal(self, s):
        return s[0] == self._SETTLED

    def legal_actions(self, s, i):
        phase = s[0]
        if i == 0:
            if phase == self._READING:
                return ("acknowledge", "defend")
            if phase == self._RESPONDING:
                return ("noop",)
            return ("noop",)
        else:
            if phase == self._READING:
                return ("noop",)
            if phase == self._RESPONDING:
                return ("continue_protest", "settle_down")
            return ("noop",)

    def transition(self, s, a):
        phase, mood = s
        t_act, c_act = a

        if phase == self._READING:
            if t_act == "acknowledge":
                return {
                    ((self._RESPONDING, self._GIGGLING), ("giggling", "acknowledged")): 0.5,
                    ((self._RESPONDING, self._PROTESTING), ("protesting", "acknowledged")): 0.5,
                }
            else:  # defend
                return {
                    ((self._RESPONDING, self._GIGGLING), ("giggling", "defended")): 0.5,
                    ((self._RESPONDING, self._PROTESTING), ("protesting", "defended")): 0.5,
                }

        if phase == self._RESPONDING:
            if c_act == "settle_down":
                return {
                    ((self._SETTLED, self._CALM), ("calm", "settled")): 1.0,
                }
            else:  # continue_protest
                return {
                    ((self._RESPONDING, self._PROTESTING), ("protesting", "none")): 0.7,
                    ((self._SETTLED, self._CALM), ("calm", "none")): 0.3,
                }

        # settled
        return {
            ((self._SETTLED, self._CALM), ("calm", "none")): 1.0,
        }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
