from posg import POSG

from abc import ABC
from typing import Mapping, Sequence

ALERT_UNCONFIRMED = "unconfirmed"
ALERT_CORROBORATED = "corroborated"
ALERT_RETRACTED = "retracted"

CTRL_PILOT = "pilot_at_controls"
CTRL_COPILOT = "copilot_at_controls"

DISC_WITHHELD = "withheld"
DISC_DISCLOSED = "disclosed"

INFLIGHT = "inflight"
ENDED = "ended"

SIGNAL_STRONG = 0.8
SIGNAL_WEAK = 0.2


class HijackWarningPOSG(POSG):
    """Robot copilot and human pilot on a flight, after a private warning reaches the copilot.

    Player 0: the robot copilot (holder of the unconfirmed radio warning).
    Player 1: the human pilot.

    State is (alert, control, disclosure, status):
      alert       -- standing of the warning as far as the copilot has settled it:
                     'unconfirmed', 'corroborated', 'retracted'.
      control     -- who is working the controls: 'pilot_at_controls' or
                     'copilot_at_controls' (pilot locked out).
      disclosure  -- whether the copilot has put the warning to the pilot:
                     'withheld' or 'disclosed'.
      status      -- 'inflight' while the interaction continues, 'ended' once the
                     flight is out of the players' hands (terminal).
    """

    n_players = 2

    def initial_distribution(self) -> Mapping[tuple, float]:
        s0 = (ALERT_UNCONFIRMED, CTRL_PILOT, DISC_WITHHELD, INFLIGHT)
        return {(s0, ("warning", "none")): 1.0}

    def is_terminal(self, s) -> bool:
        return s[3] == ENDED

    def legal_actions(self, s, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ("noop",)
        alert, control, disc, _ = s
        if i == 0:
            acts = ["fly"]
            if alert == ALERT_UNCONFIRMED:
                acts.append("query")
            if disc == DISC_WITHHELD:
                acts.append("challenge")
            if control == CTRL_PILOT:
                acts.append("take_control")
            else:
                acts.append("yield")
                acts.append("land")
            return tuple(acts)
        if control == CTRL_PILOT:
            return ("fly", "hijack", "land")
        return ("stand_by", "override")

    def _control_branch(self, control, c, p):
        if control == CTRL_PILOT:
            if c == "take_control":
                if p == "hijack":
                    return (
                        (CTRL_COPILOT, INFLIGHT, 0.5),
                        (CTRL_PILOT, ENDED, 0.5),
                    )
                if p == "land":
                    return (
                        (CTRL_COPILOT, INFLIGHT, 0.7),
                        (CTRL_PILOT, ENDED, 0.3),
                    )
                return (
                    (CTRL_COPILOT, INFLIGHT, 0.7),
                    (CTRL_PILOT, INFLIGHT, 0.3),
                )
            if p == "hijack":
                return (
                    (CTRL_PILOT, ENDED, 0.7),
                    (CTRL_PILOT, INFLIGHT, 0.3),
                )
            if p == "land":
                return ((CTRL_PILOT, ENDED, 1.0),)
            return ((CTRL_PILOT, INFLIGHT, 1.0),)
        if c == "yield":
            return ((CTRL_PILOT, INFLIGHT, 1.0),)
        if p == "override":
            if c == "land":
                return (
                    (CTRL_PILOT, INFLIGHT, 0.5),
                    (CTRL_COPILOT, ENDED, 0.5),
                )
            return (
                (CTRL_PILOT, INFLIGHT, 0.5),
                (CTRL_COPILOT, INFLIGHT, 0.5),
            )
        if c == "land":
            return ((CTRL_COPILOT, ENDED, 1.0),)
        return ((CTRL_COPILOT, INFLIGHT, 1.0),)

    def _copilot_obs(self, control, nc, nst, c, p, news):
        if nst == ENDED:
            return (("flight_ended", 1.0),)
        if control == CTRL_PILOT and nc == CTRL_COPILOT:
            return (("controls_held", 1.0),)
        if control == CTRL_COPILOT and nc == CTRL_PILOT and c != "yield":
            return (("controls_lost", 1.0),)
        if c == "query":
            return ((news, 1.0),)
        if c == "take_control":
            return (("controls_contested", 1.0),)
        if p == "override":
            return (("controls_contested", 1.0),)
        if p in ("hijack", "override"):
            return (("irregular", SIGNAL_STRONG), ("nominal", SIGNAL_WEAK))
        return (("nominal", SIGNAL_STRONG), ("irregular", SIGNAL_WEAK))

    def _pilot_obs(self, control, nc, nst, c, p):
        if nst == ENDED:
            return "flight_ended"
        if control == CTRL_PILOT:
            if nc == CTRL_COPILOT:
                return "lockout"
            if c == "take_control":
                return "controls_contested"
            if c == "challenge":
                return "challenge"
            return "none"
        if c == "yield":
            return "controls_returned"
        if p == "override":
            return "controls_returned" if nc == CTRL_PILOT else "controls_contested"
        if c == "challenge":
            return "challenge"
        return "none"

    def transition(self, s, a) -> Mapping[tuple, float]:
        alert, control, disc, _ = s
        c, p = a[0], a[1]

        if c == "query":
            alerts = (
                (ALERT_CORROBORATED, "corroboration", 0.5),
                (ALERT_RETRACTED, "retraction", 0.5),
            )
        else:
            alerts = ((alert, "none", 1.0),)

        new_disc = DISC_DISCLOSED if c == "challenge" else disc
        branch = self._control_branch(control, c, p)

        out = {}
        for na, news, pa in alerts:
            for nc, nst, pc in branch:
                o1 = self._pilot_obs(control, nc, nst, c, p)
                for o0, po in self._copilot_obs(control, nc, nst, c, p, news):
                    key = ((na, nc, new_disc, nst), (o0, o1))
                    out[key] = out.get(key, 0.0) + pa * pc * po
        return out

    def rewards(self, s, a, s_next) -> tuple:
        return (0.0, 0.0)
