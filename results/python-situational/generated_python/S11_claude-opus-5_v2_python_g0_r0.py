from posg import POSG

RIDERS = (1, 2, 3, 4)


def _shares(k):
    """k probabilities, as equal as two decimals allow, larger ones first."""
    q, rem = divmod(100, k)
    return tuple([(q + 1) / 100.0] * rem + [q / 100.0] * (k - rem))


class ShuttleStopPOSG(POSG):
    """Boarding contest at a shuttle stop with fewer seats than waiting people.

    Player 0 is the self-driving shuttle.
    Player 1 is the person leaning on a cane.
    Player 2 is the person holding a small child.
    Player 3 is the person who says she is late for work.
    Player 4 is the person who has been waiting at the stop the longest.

    State is a tuple (door, s1, s2, s3, s4):
      door  -- 'doors_shut'  : shuttle standing at the stop, doors not yet open
               'doors_open'  : doors open, a seat is still to be had
               'departed'    : shuttle has pulled away (terminal)
      s1..s4 -- condition of each waiting person, in player-index order:
               'waiting' : at the stop, has said nothing
               'voiced'  : at the stop, has stated a reason to be taken
               'aboard'  : has a seat

    Whether a seat is still left after someone is taken on is never told to
    anyone in advance: it is resolved in the transition, after everybody has
    committed, and shows up only as the shuttle closing up and pulling away.
    """

    n_players = 5

    def initial_distribution(self):
        s = ('doors_shut', 'waiting', 'waiting', 'voiced', 'waiting')
        o = ('claim_voiced', 'doors_shut', 'doors_shut', 'doors_shut', 'doors_shut')
        return {(s, o): 1.0}

    def is_terminal(self, s):
        return s[0] == 'departed'

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ('noop',)
        door = s[0]
        if i == 0:
            if door == 'doors_shut':
                return ('open_doors',)
            return ('hold_doors', 'close_doors')
        st = s[i]
        if st == 'aboard':
            return ('noop',)
        if door == 'doors_shut':
            if st == 'waiting':
                return ('state_claim', 'hold_back')
            return ('hold_back',)
        if st == 'waiting':
            return ('board', 'state_claim', 'hold_back')
        return ('board', 'hold_back')

    def transition(self, s, a):
        door = s[0]
        statuses = list(s[1:])
        claimed = False
        for idx, i in enumerate(RIDERS):
            if a[i] == 'state_claim' and statuses[idx] == 'waiting':
                statuses[idx] = 'voiced'
                claimed = True

        if door == 'doors_shut':
            ns = ('doors_open',) + tuple(statuses)
            shuttle_obs = 'claim_voiced' if claimed else 'none'
            obs = (shuttle_obs,) + tuple('doors_open' for _ in RIDERS)
            return {(ns, obs): 1.0}

        if a[0] == 'close_doors':
            ns = ('departed',) + tuple(statuses)
            obs = ('departed',) + tuple('departed' for _ in RIDERS)
            return {(ns, obs): 1.0}

        boarders = [idx for idx, i in enumerate(RIDERS) if a[i] == 'board']

        if not boarders:
            ns = ('doors_open',) + tuple(statuses)
            shuttle_obs = 'claim_voiced' if claimed else 'none'
            obs = (shuttle_obs,) + tuple('none' for _ in RIDERS)
            return {(ns, obs): 1.0}

        outcomes = []
        for idx in boarders:
            for door_next in ('doors_open', 'departed'):
                new_statuses = list(statuses)
                new_statuses[idx] = 'aboard'
                ns = (door_next,) + tuple(new_statuses)
                rider_obs = []
                for j in range(len(RIDERS)):
                    if j == idx:
                        rider_obs.append('aboard')
                    elif door_next == 'departed':
                        rider_obs.append('departed')
                    else:
                        rider_obs.append('none')
                shuttle_obs = 'departed' if door_next == 'departed' else 'boarder_admitted'
                outcomes.append((ns, (shuttle_obs,) + tuple(rider_obs)))

        shares = _shares(len(outcomes))
        dist = {}
        for key, p in zip(outcomes, shares):
            dist[key] = dist.get(key, 0.0) + p
        return dist

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0, 0.0)
