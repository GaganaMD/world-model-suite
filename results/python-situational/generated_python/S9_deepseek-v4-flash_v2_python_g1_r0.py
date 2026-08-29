from posg import POSG

class CareRobotFamilyGame(POSG[str, str, str]):
    """3-player POSG:

    Player 0: Daughter
    Player 1: Son
    Player 2: Elderly Man

    States:
      'home'       – non-terminal; all three are present, each has expressed their wish
      'go_out'     – terminal; man leaves with son
      'stay_home'  – terminal; man stays home with daughter

    Actions:
      Daughter: 'advocate_stay'
      Son:      'advocate_go'
      Man:      'express_go'

    Observations:
      'none' – initial step
      'went' – man left
      'stayed' – man stayed
    """
    n_players = 3

    def initial_distribution(self):
        return {('home', ('none', 'none', 'none')): 1.0}

    def is_terminal(self, s: str) -> bool:
        return s != 'home'

    def legal_actions(self, s: str, i: int):
        if s != 'home':
            return ()
        if i == 0:
            return ('advocate_stay',)
        elif i == 1:
            return ('advocate_go',)
        elif i == 2:
            return ('express_go',)

    def transition(self, s: str, a):
        # Only called for s == 'home'.
        # The man looks tired → staying more likely.
        return {
            ('go_out', ('went', 'went', 'went')): 0.4,
            ('stay_home', ('stayed', 'stayed', 'stayed')): 0.6
        }

    def rewards(self, s: str, a, s_next: str):
        return (0.0, 0.0, 0.0)
