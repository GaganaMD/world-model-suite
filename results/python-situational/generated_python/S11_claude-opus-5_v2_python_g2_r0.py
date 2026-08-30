from posg import POSG

ADMIT_ACTIONS = ('admit_elder', 'admit_parent', 'admit_commuter', 'admit_teen')
WAITERS = (1, 2, 3, 4)


class ShuttleAtBusyStopPOSG(POSG):
    """Boarding contest at a stop where the arriving self-driving shuttle has
    less room than there are people waiting.

    Players:
      0 - the self-driving shuttle (it opens for one person at a time, holds
          with its doors open, or shuts its doors and pulls away)
      1 - the elderly person leaning on a cane
      2 - the parent holding a small child
      3 - the commuter who says she is late for work
      4 - the teenager who has been waiting at the stop the longest

    State tuple (same order always):
      s[0] - whether the shuttle still has room and its doors are open
             ('room') or it has pulled away ('departed', terminal)
      s[1] - the elderly person's condition: 'silent' (has not stated a case),
             'voiced' (has stated a case), 'aboard'
      s[2] - the parent's condition, same values
      s[3] - the commuter's condition, same values
      s[4] - the teenager's condition, same values

    Whether room remains after someone boards is settled only after everyone
    has committed, and the people at the stop cannot tell room-remaining from
    room-gone except by the doors shutting.
    """

    n_players = 5

    def initial_distribution(self):
        s = ('room', 'silent', 'silent', 'voiced', 'silent')
        o = ('claims_voiced', 'claims_voiced', 'claims_voiced', 'none', 'claims_voiced')
        return {(s, o): 1.0}

    def is_terminal(self, s):
        return s[0] == 'departed'

    def legal_actions(self, s, i):
        if i == 0:
            acts = []
            for j in WAITERS:
                if s[j] != 'aboard':
                    acts.append(ADMIT_ACTIONS[j - 1])
            acts.append('hold')
            acts.append('depart')
            return tuple(acts)
        st = s[i]
        if st == 'aboard':
            return ('noop',)
        if st == 'silent':
            return ('press', 'speak', 'wait')
        return ('press', 'wait')

    def transition(self, s, a):
        sh = a[0]
        statuses = list(s[1:])

        if sh == 'depart':
            ns = ('departed',) + tuple(statuses)
            o = ('doors_shut',) * 5
            return {(ns, o): 1.0}

        speakers = tuple(j for j in WAITERS if s[j] == 'silent' and a[j] == 'speak')

        if sh == 'hold':
            new = list(statuses)
            for j in speakers:
                new[j - 1] = 'voiced'
            ns = ('room',) + tuple(new)
            obs = ['claims_voiced' if speakers else 'none']
            for j in WAITERS:
                others = tuple(k for k in speakers if k != j)
                obs.append('claims_voiced' if others else 'none')
            return {(ns, tuple(obs)): 1.0}

        t = ADMIT_ACTIONS.index(sh) + 1

        base = list(statuses)
        for j in speakers:
            if j != t:
                base[j - 1] = 'voiced'

        boarded = list(base)
        boarded[t - 1] = 'aboard'

        stay = list(base)
        if t in speakers:
            stay[t - 1] = 'voiced'

        o_cont = ['rider_boarded']
        for j in WAITERS:
            o_cont.append('boarded' if j == t else 'another_boarded')
        o_cont = tuple(o_cont)

        o_fill = ['room_gone']
        for j in WAITERS:
            o_fill.append('boarded' if j == t else 'doors_shut')
        o_fill = tuple(o_fill)

        o_stay = ['no_boarding']
        for j in WAITERS:
            o_stay.append('admitted' if j == t else 'another_admitted')
        o_stay = tuple(o_stay)

        s_cont = ('room',) + tuple(boarded)
        s_fill = ('departed',) + tuple(boarded)
        s_stay = ('room',) + tuple(stay)

        if a[t] == 'press':
            return {
                (s_cont, o_cont): 0.5,
                (s_fill, o_fill): 0.5,
            }
        return {
            (s_stay, o_stay): 0.5,
            (s_cont, o_cont): 0.25,
            (s_fill, o_fill): 0.25,
        }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0, 0.0)
