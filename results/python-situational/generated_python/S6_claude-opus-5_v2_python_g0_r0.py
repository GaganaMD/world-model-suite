from posg import POSG

_TAKE = "take"
_REFUSE = "refuse"
_TURN_AWAY = "turn_away"
_NOOP = "noop"
_REMIND = "remind"
_WAIT = "wait"
_LET_BE = "let_be"

_PENDING = "pending"
_TAKEN = "taken"
_DECLINED = "declined"

_UNPROMPTED = "unprompted"
_PROMPTED = "prompted"
_REFUSING = "refusing"
_TURNED_AWAY = "turned_away"
_SETTLED = "settled"

_ROBOT_OBS = {
    _TAKE: "dose_taken",
    _REFUSE: "refusal",
    _TURN_AWAY: "withdrawal",
    _NOOP: "none",
}


class MedicationRefusalPOSG(POSG):
    """Elder-care robot and resident over an untaken evening dose.

    Player 0 is the care robot; player 1 is the resident.

    A state is a pair (dose, stance):
      dose   -- 'pending'  the dose is still outstanding
                'taken'    the resident has taken the dose
                'declined' the dose has been left with the robot no longer pressing
      stance -- 'unprompted'  the resident has not been spoken to about the dose
                'prompted'    the resident has been addressed, stance unstated
                'refusing'    the resident has voiced refusal
                'turned_away' the resident has turned away from the robot
                'settled'     the episode is closed (terminal)

    Robot acts: 'remind' (voice the dose), 'wait' (hold off), 'let_be' (stop
    pressing the matter), 'noop'.
    Resident acts: 'take', 'refuse', 'turn_away', 'noop'.

    Robot observations: 'dose_pending', 'dose_taken', 'refusal', 'withdrawal',
    'none'.  The robot cannot tell whether a reminder registered.
    Resident observations: 'reminder', 'none'.
    """

    n_players = 2

    def initial_distribution(self):
        return {((_PENDING, _UNPROMPTED), ("dose_pending", "none")): 1.0}

    def is_terminal(self, s):
        return s[1] == _SETTLED

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return (_NOOP,)
        stance = s[1]
        if i == 0:
            if stance == _UNPROMPTED:
                return (_REMIND, _WAIT)
            if stance == _PROMPTED:
                return (_REMIND, _WAIT)
            return (_REMIND, _WAIT, _LET_BE)
        if stance == _UNPROMPTED:
            return (_NOOP,)
        return (_TAKE, _REFUSE, _TURN_AWAY)

    @staticmethod
    def _stance_after(res_a):
        if res_a == _TAKE:
            return (_TAKEN, _SETTLED)
        if res_a == _REFUSE:
            return (_PENDING, _REFUSING)
        return (_PENDING, _TURNED_AWAY)

    def transition(self, s, a):
        robot_a, res_a = a[0], a[1]
        stance = s[1]

        if stance == _UNPROMPTED:
            if robot_a == _WAIT:
                return {(s, ("none", "none")): 1.0}
            return {
                ((_PENDING, _PROMPTED), ("none", "reminder")): 0.8,
                ((_PENDING, _UNPROMPTED), ("none", "none")): 0.2,
            }

        robot_obs = _ROBOT_OBS[res_a]

        if robot_a == _LET_BE:
            nxt = (_TAKEN, _SETTLED) if res_a == _TAKE else (_DECLINED, _SETTLED)
            return {(nxt, (robot_obs, "none")): 1.0}

        nxt = self._stance_after(res_a)

        if robot_a == _WAIT:
            return {(nxt, (robot_obs, "none")): 1.0}

        p = 0.5 if stance == _TURNED_AWAY else 0.8
        return {
            (nxt, (robot_obs, "reminder")): p,
            (nxt, (robot_obs, "none")): round(1.0 - p, 2),
        }

    def rewards(self, s, a, s_next):
        return (0.0, 0.0)
