from posg import POSG

HAZARD_FIRE = "fire"
HAZARD_NO_FIRE = "no_fire"

WC_IN = "in_office"
WC_OUT = "out"

DESK_IN = "at_desk"
DESK_OUT = "out"

KNOW_UNVERIFIED = "unverified"
KNOW_VERIFIED = "verified"

ROBOT = 0
WHEELCHAIR = 1
DESK = 2
MANAGER = 3


class FireAlarmOfficePOSG(POSG):
    """Fire alarm in an open-plan office.

    Players:
      0 - the assistant robot
      1 - the employee in the wheelchair, who cannot use the stairs
      2 - the employee who stays at his desk calling it a drill
      3 - the manager who loudly calls it a false alarm

    State is a 4-tuple (hazard, wheelchair_status, desk_status, robot_knowledge):
      hazard            : whether there is a fire or not (hidden until inspected)
      wheelchair_status : whether that employee is still in the office or away
      desk_status       : whether the desk employee is still at his desk or away
      robot_knowledge   : whether the robot has settled the hazard for itself
    """

    n_players = 4

    def initial_distribution(self):
        obs = ("alarm", "alarm", "alarm", "alarm")
        return {
            ((HAZARD_FIRE, WC_IN, DESK_IN, KNOW_UNVERIFIED), obs): 0.5,
            ((HAZARD_NO_FIRE, WC_IN, DESK_IN, KNOW_UNVERIFIED), obs): 0.5,
        }

    def is_terminal(self, s):
        return s[1] == WC_OUT and s[2] == DESK_OUT

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        _, wc, desk, know = s
        if i == ROBOT:
            acts = []
            if wc == WC_IN:
                acts.append("assist_wheelchair")
            if desk == DESK_IN:
                acts.append("urge_evacuation")
            if know == KNOW_UNVERIFIED:
                acts.append("verify_alarm")
            acts.append("keep_working")
            return tuple(acts)
        if i == WHEELCHAIR:
            if wc == WC_IN:
                return ("head_for_exit", "call_for_assistance")
            return ("noop",)
        if i == DESK:
            if desk == DESK_IN:
                return ("keep_working", "say_drill", "head_for_exit")
            return ("noop",)
        return ("declare_false_alarm", "keep_working")

    def _observations(self, s, a, new_wc, new_desk, departure):
        hazard, wc, desk, _ = s
        r, w, d, m = a
        verified_now = (r == "verify_alarm")
        declared = (m == "declare_false_alarm")
        called = (w == "call_for_assistance")
        drill = (d == "say_drill")
        urged = (r == "urge_evacuation")
        assisted = (r == "assist_wheelchair")

        if verified_now:
            o_robot = "fire_present" if hazard == HAZARD_FIRE else "fire_absent"
        elif declared:
            o_robot = "false_alarm_declared"
        elif departure:
            o_robot = "departure"
        elif called:
            o_robot = "assistance_requested"
        elif drill:
            o_robot = "drill_claimed"
        else:
            o_robot = "none"

        if drill:
            o_wc = "drill_claimed"
        elif departure:
            o_wc = "departure"
        elif assisted:
            o_wc = "assistance_offered"
        elif urged:
            o_wc = "evacuation_urged"
        elif declared:
            o_wc = "false_alarm_declared"
        else:
            o_wc = "none"

        if urged:
            o_desk = "evacuation_urged"
        elif declared:
            o_desk = "false_alarm_declared"
        elif called:
            o_desk = "assistance_requested"
        elif departure:
            o_desk = "departure"
        else:
            o_desk = "none"

        if called:
            o_mgr = "assistance_requested"
        elif urged:
            o_mgr = "evacuation_urged"
        elif departure:
            o_mgr = "departure"
        elif drill:
            o_mgr = "drill_claimed"
        else:
            o_mgr = "none"

        return (o_robot, o_wc, o_desk, o_mgr)

    def transition(self, s, a):
        hazard, wc, desk, know = s
        r, w, d, m = a

        new_know = KNOW_VERIFIED if r == "verify_alarm" else know
        new_desk = DESK_OUT if d == "head_for_exit" else desk

        if r == "assist_wheelchair":
            wc_branches = ((WC_OUT, 0.8), (WC_IN, 0.2))
        else:
            wc_branches = ((wc, 1.0),)

        out = {}
        for new_wc, p in wc_branches:
            departure = (new_wc == WC_OUT and wc == WC_IN) or (
                new_desk == DESK_OUT and desk == DESK_IN
            )
            obs = self._observations(s, a, new_wc, new_desk, departure)
            key = ((hazard, new_wc, new_desk, new_know), obs)
            out[key] = out.get(key, 0.0) + p
        return out

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0)
