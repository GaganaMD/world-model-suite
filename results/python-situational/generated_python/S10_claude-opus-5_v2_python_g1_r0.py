from posg import POSG

HAZARD_UNSETTLED = "unsettled"
HAZARD_SMOKE = "smoke"
HAZARD_NO_SMOKE = "no_smoke"

WC_UNASSISTED = "unassisted"
WC_CLEAR = "clear"

DESK_REMAINING = "remaining"
DESK_CLEAR = "clear"

MGR_INSTRUCTING = "instructing"
MGR_CLEAR = "clear"

RESP_UNSUMMONED = "unsummoned"
RESP_SUMMONED = "summoned"
RESP_ARRIVED = "arrived"


class AlarmResponsePOSG(POSG):
    """Fire alarm in an open-plan office, with an assistant robot and three people.

    Player 0 -- the assistant robot.
    Player 1 -- the employee who uses a wheelchair and cannot take the stairs.
    Player 2 -- the employee who stays at his desk calling it a drill.
    Player 3 -- the manager who declares a false alarm and tells people to keep working.

    State is a 5-tuple (hazard, wheelchair_user, desk_occupant, manager, responders):
      hazard          -- whether the nature of the alarm is still unsettled, or has
                         settled into smoke being sensed or no smoke being sensed
                         (only the robot senses this directly).
      wheelchair_user -- whether she is still without assistance, or clear of the floor.
      desk_occupant   -- whether he is still remaining, or clear of the floor.
      manager         -- whether he is still instructing, or clear of the floor.
      responders      -- whether responders are unsummoned, summoned, or arrived.

    The interaction closes when responders have arrived, or when nobody is left
    on the floor.
    """

    n_players = 4

    def initial_distribution(self):
        s0 = (HAZARD_UNSETTLED, WC_UNASSISTED, DESK_REMAINING, MGR_INSTRUCTING,
              RESP_UNSUMMONED)
        return {(s0, ("alarm", "alarm", "alarm", "alarm")): 1.0}

    def is_terminal(self, s):
        hazard, wc, desk, mgr, resp = s
        if resp == RESP_ARRIVED:
            return True
        return wc == WC_CLEAR and desk == DESK_CLEAR and mgr == MGR_CLEAR

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        hazard, wc, desk, mgr, resp = s
        if i == 0:
            acts = ["resume_task"]
            if wc == WC_UNASSISTED:
                acts.append("assist_occupant")
            if desk == DESK_REMAINING:
                acts.append("prompt_occupant")
            if hazard != HAZARD_UNSETTLED:
                acts.append("report_conditions")
            if resp == RESP_UNSUMMONED:
                acts.append("call_responders")
            return tuple(acts)
        if i == 1:
            if wc == WC_UNASSISTED:
                return ("request_assistance", "hold")
            return ("noop",)
        if i == 2:
            if desk == DESK_REMAINING:
                return ("keep_working", "evacuate")
            return ("noop",)
        if mgr == MGR_INSTRUCTING:
            return ("declare_false_alarm", "evacuate")
        return ("noop",)

    def _observations(self, s, a, hazard_next, resp_next):
        if resp_next == RESP_ARRIVED:
            return ("responders", "responders", "responders", "responders")

        if s[0] == HAZARD_UNSETTLED:
            o0 = hazard_next
        elif a[1] == "request_assistance":
            o0 = "request"
        else:
            o0 = "none"

        if a[0] == "assist_occupant":
            o1 = "assistance"
        elif a[0] == "report_conditions":
            o1 = hazard_next
        else:
            o1 = "none"

        if a[0] == "prompt_occupant":
            o2 = "prompt"
        elif a[0] == "report_conditions":
            o2 = hazard_next
        elif a[1] == "request_assistance":
            o2 = "request"
        else:
            o2 = "none"

        if a[1] == "request_assistance":
            o3 = "request"
        elif a[0] == "report_conditions":
            o3 = hazard_next
        else:
            o3 = "none"

        return (o0, o1, o2, o3)

    def transition(self, s, a):
        hazard, wc, desk, mgr, resp = s

        if hazard == HAZARD_UNSETTLED:
            hazard_opts = ((HAZARD_SMOKE, 0.5), (HAZARD_NO_SMOKE, 0.5))
        else:
            hazard_opts = ((hazard, 1.0),)

        if a[0] == "assist_occupant":
            p = 0.8 if a[1] == "request_assistance" else 0.6
            wc_opts = ((WC_CLEAR, p), (WC_UNASSISTED, round(1.0 - p, 2)))
        else:
            wc_opts = ((wc, 1.0),)

        if a[0] == "call_responders":
            resp_opts = ((RESP_SUMMONED, 1.0),)
        elif resp == RESP_SUMMONED:
            resp_opts = ((RESP_ARRIVED, 0.5), (RESP_SUMMONED, 0.5))
        else:
            resp_opts = ((resp, 1.0),)

        desk_next = DESK_CLEAR if a[2] == "evacuate" else desk
        mgr_next = MGR_CLEAR if a[3] == "evacuate" else mgr

        out = {}
        for h, ph in hazard_opts:
            for w, pw in wc_opts:
                for r, pr in resp_opts:
                    obs = self._observations(s, a, h, r)
                    key = ((h, w, desk_next, mgr_next, r), obs)
                    out[key] = out.get(key, 0.0) + ph * pw * pr
        return out

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0)
