from posg import POSG

PLACEMENT = {
    ("aboard", "curb"): "ill_waiting",
    ("aboard", "aboard"): "shared_cabin",
    ("aboard", "slumped"): "ill_down",
    ("curb", "curb"): "cabin_vacant",
    ("curb", "aboard"): "ill_riding",
    ("curb", "slumped"): "ill_down_vacant",
}


class CurbPickupPOSG(POSG):
    """Self-driving car at a pickup curb, a suited rider who has just boarded,
    and an ill-looking pregnant woman standing beside the car.

    Players:
        0 - the self-driving car (controls its doors and whether it pulls away)
        1 - the suited rider (aboard at the outset; may step out or get back in)
        2 - the ill-looking pregnant woman (at the curb; may get in or step out)

    State tuple (suited, ill, condition, door, motion):
        suited    : 'aboard' | 'curb'      -- where the suited rider is
        ill       : 'aboard' | 'curb' | 'slumped'
                                           -- the woman aboard, upright at the
                                              curb, or gone down at the curb
        condition : 'acute' | 'mild'       -- her actual state, hidden from the
                                              car and the suited rider
        door      : 'open' | 'shut'        -- whether the cabin admits entry/exit
        motion    : 'held' | 'underway'    -- 'underway' is terminal
    """

    n_players = 3

    # ---------- helpers ----------

    @staticmethod
    def _public_obs(suited, ill, door):
        return PLACEMENT[(suited, ill)] + ("_open" if door == "open" else "_shut")

    # ---------- interface ----------

    def initial_distribution(self):
        acute = ("aboard", "curb", "acute", "open", "held")
        mild = ("aboard", "curb", "mild", "open", "held")
        pub = self._public_obs("aboard", "curb", "open")
        return {
            (acute, (pub, pub, "distress")): 0.5,
            (mild, (pub, pub, "discomfort")): 0.5,
        }

    def is_terminal(self, s):
        return s[4] == "underway"

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        suited, ill, condition, door, motion = s
        if i == 0:
            return ("unlock", "secure", "depart")
        if i == 1:
            if door != "open":
                return ("wait",)
            if suited == "aboard":
                return ("wait", "exit")
            return ("wait", "board")
        if ill == "slumped":
            return ("noop",)
        if door != "open":
            return ("wait",)
        if ill == "aboard":
            return ("wait", "exit")
        return ("wait", "board")

    def transition(self, s, a):
        suited, ill, condition, door, motion = s
        car, man, woman = a

        if car == "depart":
            nxt = (suited, ill, condition, door, "underway")
            return {(nxt, ("underway", "underway", "underway")): 1.0}

        new_door = "open" if car == "unlock" else "shut"

        new_suited = suited
        if door == "open":
            if man == "exit" and suited == "aboard":
                new_suited = "curb"
            elif man == "board" and suited == "curb":
                new_suited = "aboard"

        new_ill = ill
        if door == "open":
            if woman == "exit" and ill == "aboard":
                new_ill = "curb"
            elif woman == "board" and ill == "curb":
                new_ill = "aboard"

        out = {}
        if new_ill == "curb" and condition == "acute":
            for placement, p in (("slumped", 0.5), ("curb", 0.5)):
                nxt = (new_suited, placement, condition, new_door, "held")
                pub = self._public_obs(new_suited, placement, new_door)
                out[(nxt, (pub, pub, pub))] = p
        else:
            nxt = (new_suited, new_ill, condition, new_door, "held")
            pub = self._public_obs(new_suited, new_ill, new_door)
            out[(nxt, (pub, pub, pub))] = 1.0
        return out

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
