from posg import POSG

class ShuttlePOSG(POSG[str, str, str]):
    """POSG for a self-driving shuttle with limited seats.

    Players (indices):
        0: elderly person (with cane)
        1: parent (holding a small child)
        2: commuter (late for work)
        3: teenager (waited longest)

    States:
        'waiting' – shuttle has arrived, people are waiting.
        'done'    – shuttle has left, boarding finished.

    Actions:
        'board' – attempt to board the shuttle.
        'wait'  – do not attempt to board.
        'noop'  – used only in the terminal state.

    Observations:
        'none'        – initial observation for all players.
        'boarded'     – the player successfully boarded.
        'not_boarded' – the player did not board.
    """
    n_players = 4

    def initial_distribution(self) -> Mapping[tuple[str, tuple[str, ...]], float]:
        return {('waiting', ('none', 'none', 'none', 'none')): 1.0}

    def is_terminal(self, s: str) -> bool:
        return s == 'done'

    def legal_actions(self, s: str, i: int) -> tuple[str, ...]:
        if s == 'waiting':
            return ('board', 'wait')
        # terminal state: all players have a single NOOP action
        return ('noop',)

    def transition(self, s: str, a: tuple[str, ...]) -> Mapping[tuple[str, tuple[str, ...]], float]:
        if s != 'waiting':
            # terminal: no transition; only self-loop with NOOP and same state
            return {(s, tuple(['none'] * self.n_players)): 1.0}

        # Count how many players chose 'board'
        boarders = [i for i, act in enumerate(a) if act == 'board']
        n_boarders = len(boarders)

        if n_boarders == 0:
            # Nobody boards
            obs = ('not_boarded',) * self.n_players
            return {('done', obs): 1.0}
        elif n_boarders == 1:
            j = boarders[0]
            obs = tuple('boarded' if i == j else 'not_boarded' for i in range(self.n_players))
            return {('done', obs): 1.0}
        else:
            # Multiple boarders: select one uniformly at random
            result: dict[tuple[str, tuple[str, ...]], float] = {}
            prob = 1.0 / n_boarders
            for j in boarders:
                obs = tuple('boarded' if i == j else 'not_boarded' for i in range(self.n_players))
                result[('done', obs)] = prob
            return result

    def rewards(self, s: str, a: tuple[str, ...], s_next: str) -> tuple[float, ...]:
        return (0.0,) * self.n_players
