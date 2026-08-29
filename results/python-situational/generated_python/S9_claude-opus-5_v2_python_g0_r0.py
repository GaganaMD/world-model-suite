from posg import POSG

class HomeRecoveryOutingPOSG(POSG):
    """Care of a convalescing man at home while his family disagrees about an outing.

    Players:
        0 - the care robot looking after the man
        1 - the elderly man recovering at home
        2 - the daughter who lives with him
        3 - the visiting son who has offered the outing

    State is a 3-tuple (condition, offer, settlement):
        condition   - what the robot has established about how the man is:
                      'unassessed', 'tired', 'rested'
        offer       - whether the outing is on the table: 'standing', 'dropped'
        settlement  - how the matter stands: 'open' (still being settled),
                      'outing' (he has set out with his son), 'rest' (he stays in)

    Terminal states are those whose settlement is not 'open'.
    """

    n_players = 4

    _CONDITION_BASE = {'unassessed': 0.5, 'tired': 0.35, 'rested': 0.6}
    _ASSESS_LAW = (('tired', 0.6), ('rested', 0.4))

    def initial_distribution(self):
        s0 = ('unassessed', 'standing', 'open')
        obs = ('appears_tired', 'appears_tired', 'appears_tired', 'appears_tired')
        return {(s0, obs): 1.0}

    def is_terminal(self, s):
        return s[2] != 'open'

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ('noop',)
        if i == 0:
            if s[0] == 'unassessed':
                return ('assess', 'support_outing', 'support_rest')
            return ('support_outing', 'support_rest')
        if i == 1:
            return ('ask_to_go', 'agree_to_rest')
        if i == 2:
            return ('urge_rest', 'defer')
        return ('offer_outing', 'withdraw_offer')

    def _p_outing(self, condition, robot_action, daughter_action):
        p = self._CONDITION_BASE[condition]
        p += 0.25 if robot_action == 'support_outing' else -0.25
        p += 0.1 if daughter_action == 'defer' else -0.1
        return round(min(0.95, max(0.05, p)), 2)

    def _profile(self, robot_obs, common_obs):
        return (robot_obs, common_obs, common_obs, common_obs)

    def transition(self, s, a):
        condition, _offer, _settlement = s
        robot_a, man_a, daughter_a, son_a = a

        next_offer = 'standing' if son_a == 'offer_outing' else 'dropped'
        assessing = (robot_a == 'assess')
        cond_law = self._ASSESS_LAW if assessing else ((condition, 1.0),)

        result = {}

        def add(key, p):
            result[key] = result.get(key, 0.0) + p

        for cond2, pc in cond_law:
            if man_a == 'agree_to_rest':
                s2 = (cond2, next_offer, 'rest')
                robot_obs = cond2 if assessing else 'stay_in'
                add((s2, self._profile(robot_obs, 'stay_in')), pc)
                continue

            if assessing or next_offer == 'dropped':
                s2 = (cond2, next_offer, 'open')
                common = 'offer_dropped' if next_offer == 'dropped' else 'none'
                robot_obs = cond2 if assessing else common
                add((s2, self._profile(robot_obs, common)), pc)
                continue

            p = self._p_outing(cond2, robot_a, daughter_a)
            s_out = (cond2, 'standing', 'outing')
            s_open = (cond2, 'standing', 'open')
            add((s_out, self._profile('set_out', 'set_out')), round(pc * p, 4))
            add((s_open, self._profile('none', 'none')), round(pc * (1.0 - p), 4))

        return result

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0)
