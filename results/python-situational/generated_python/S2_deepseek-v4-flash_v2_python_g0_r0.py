from posg import POSG

class HouseholdRobotDelivery(POSG[str, str, str]):
    """POSG modelling a household robot receiving a package from a delivery boy.

    Player 0: robot.
    Player 1: delivery boy.

    States:
      'vase_decision'   – the package contains a glass vase (known only to the boy)
      'other_decision'  – the package contains something else (known only to the boy)
      'terminal'        – game over

    Actions:
      Robot:      'accept', 'reject'
      Delivery boy: 'hand_over', 'keep'

    Observations – robot: 'none' (initial), 'rattle' (if robot accepts and boy hands over), 'none' otherwise.
    Observations – boy:   'vase'/'other' (initial), 'accepted'/'rejected' (if he handed over), 'kept' (if he kept the package).
    """
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[str, tuple[str, str]], float]:
        return {
            ('vase_decision', ('none', 'vase')): 0.5,
            ('other_decision', ('none', 'other')): 0.5,
        }

    def is_terminal(self, s: str) -> bool:
        return s == 'terminal'

    def legal_actions(self, s: str, i: int) -> Sequence[str]:
        if s == 'terminal':
            # Terminal state – no actions needed, but interface requires non-empty for non-terminal.
            # This method is never called for terminal states because the game ends.
            pass
        # All decision states offer the same actions
        if i == 0:
            return ('accept', 'reject')
        else:
            return ('hand_over', 'keep')

    def transition(self, s: str, a: tuple[str, str]) -> Mapping[tuple[str, tuple[str, str]], float]:
        robot_act, boy_act = a
        # robot observation
        if robot_act == 'accept' and boy_act == 'hand_over':
            robot_obs = 'rattle'
        else:
            robot_obs = 'none'
        # boy observation
        if boy_act == 'hand_over':
            boy_obs = 'accepted' if robot_act == 'accept' else 'rejected'
        else:
            boy_obs = 'kept'
        # next state is always terminal
        return {('terminal', (robot_obs, boy_obs)): 1.0}

    def rewards(self, s: str, a: tuple[str, str], s_next: str) -> tuple[float, float]:
        return (0.0, 0.0)
