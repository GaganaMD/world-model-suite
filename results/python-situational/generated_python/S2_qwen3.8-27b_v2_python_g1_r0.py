from posg import POSG

from collections.abc import Mapping, Sequence


class VaseDelivery(POSG):
    """Two-player simultaneous-move POSG for a fragile-package hand-off.

    Player 0 = household robot.
    Player 1 = delivery boy.

    State tuple (phase, fragility):
      phase     : 'handoff' | 'done'
      fragility : 'rattling' | 'settled'

    'handoff' is the live state: the boy has the package and the robot has not yet
    taken it.  'done' is terminal: the package has been handed over and the
    interaction is closed.

    Fragility is the latent condition of the package.  It starts 'rattling'
    (the boy reports it rattles when moved) and is revealed to the robot only
    after the robot takes the package.  The boy's handling decides whether the
    package arrives 'settled' or stays 'rattling'.
    """

    n_players = 2

    # --- state helpers ---------------------------------------------------
    _PHASE_HANDOFF = "handoff"
    _PHASE_DONE = "done"
    _FRAG_RATTLE = "rattling"
    _FRAG_SETTLED = "settled"

    def _state(self, phase, fragility):
        return (phase, fragility)

    # --- initial distribution -------------------------------------------
    def initial_distribution(self) -> Mapping[tuple, float]:
        s0 = self._state(self._PHASE_HANDOFF, self._FRAG_RATTLE)
        o0 = ("rattling", "rattling")
        return {(s0, o0): 1.0}

    # --- terminality -----------------------------------------------------
    def is_terminal(self, s) -> bool:
        return s[0] == self._PHASE_DONE

    # --- legal actions ---------------------------------------------------
    def legal_actions(self, s, i) -> Sequence[str]:
        if s[0] != self._PHASE_HANDOFF:
            return ("noop",)
        if i == 0:
            return ("take_package",)
        return ("handle_gently", "handle_carelessly")

    # --- transition ------------------------------------------------------
    def transition(self, s, a) -> Mapping[tuple, float]:
        if s[0] != self._PHASE_HANDOFF:
            # terminal: nothing changes
            o = ("none", "none")
            return {((self._state(self._PHASE_DONE, s[1]), o)): 1.0}

        robot_act, boy_act = a[0], a[1]
        # The boy's handling decides the package's condition.
        if boy_act == "handle_gently":
            frag = self._FRAG_SETTLED
        else:
            frag = self._FRAG_RATTLE

        s_next = self._state(self._PHASE_DONE, frag)
        # The robot learns the condition only by taking the package.
        robot_obs = frag
        boy_obs = "handed_over"
        o = (robot_obs, boy_obs)
        return {((s_next, o)): 1.0}

    # --- rewards ---------------------------------------------------------
    def rewards(self, s, a, s_next) -> tuple:
        return (0.0, 0.0)
