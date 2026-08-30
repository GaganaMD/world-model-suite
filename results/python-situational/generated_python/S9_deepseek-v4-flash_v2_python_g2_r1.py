from posg import POSG

DECISION_VALUES = ('go', 'stay')

class CareRobotPOSG(POSG):
    """Four players: 0=man, 1=daughter, 2=son, 3=robot.
    States: 'home_tired' (non-terminal), 'stayed_home' (terminal), 'went_out' (terminal).
    The man is tired and looks tired; the robot knows his true state.
    """
    n_players = 4

    def initial_distribution(self):
        # state home_tired, observations: man sees 'tired', daughter/son see 'looks_tired', robot sees 'tired'
        obs = ('tired', 'looks_tired', 'looks_tired', 'tired')
        return {('home_tired', obs): 1.0}

    def is_terminal(self, s):
        return s in ('stayed_home', 'went_out')

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ()  # not called for terminal states per interface, but safe
        if i == 0:  # man
            return DECISION_VALUES
        elif i == 1:  # daughter
            return ('insist_stay',)
        elif i == 2:  # son
            return ('offer_go',)
        elif i == 3:  # robot
            return ('allow', 'restrict')
        else:
            raise ValueError

    def transition(self, s, a):
        if s != 'home_tired':
            return {}  # terminal, not called
        man_act, daughter_act, son_act, robot_act = a
        # Only man and robot matter for transition
        if man_act == 'stay':
            next_s = 'stayed_home'
        elif man_act == 'go':
            if robot_act == 'allow':
                next_s = 'went_out'
            else:  # restrict
                next_s = 'stayed_home'
        else:
            raise ValueError
        # Observations: after transition, everyone sees the outcome
        # Man knows his own action and outcome, but we give same observation to all for simplicity
        obs = ('none', 'none', 'none', 'none')
        return {(next_s, obs): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0)
