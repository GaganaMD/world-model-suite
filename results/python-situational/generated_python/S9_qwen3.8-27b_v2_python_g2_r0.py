from posg import POSG

class CareDecision(POSG):
    """
    n_players = 3
    Player 0: the man (the patient)
    Player 1: the daughter (lives with him)
    Player 2: the son (visiting for the day)

    State tuple: (fatigue, decision)
      fatigue : 'low' | 'high'   -- the man's current level of tiredness
      decision: 'open' | 'gather' | 'rest'
               'open'   -- the man has not yet made his choice
               'gather' -- the man chose to go to the family gathering
               'rest'   -- the man chose to stay home and rest

    The man acts only while the decision is open; the daughter and son act only
    while the decision is open.  Once the man decides, the interaction is over.
    """

    n_players = 3

    # ---- helpers -----------------------------------------------------------

    def _obs(self, s):
        fatigue, decision = s
        if decision == 'open':
            return ('tired' if fatigue == 'high' else 'well', 'none', 'none')
        return (decision, decision, decision)

    # ---- required methods --------------------------------------------------

    def initial_distribution(self):
        return {
            (('low', 'open'), ('well', 'none', 'none')): 0.5,
            (('high', 'open'), ('tired', 'none', 'none')): 0.5,
        }

    def is_terminal(self, s):
        return s[1] != 'open'

    def legal_actions(self, s, i):
        if s[1] != 'open':
            return ('noop',)
        if i == 0:
            return ('go', 'stay')
        if i == 1:
            return ('urge_rest', 'allow_go')
        return ('offer_trip', 'hold_back')

    def transition(self, s, a):
        fatigue, decision = s
        if decision != 'open':
            return {(s, self._obs(s)): 1.0}

        man_act = a[0]
        if man_act == 'go':
            nxt = (fatigue, 'gather')
        else:
            nxt = (fatigue, 'rest')
        return {(nxt, self._obs(nxt)): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
