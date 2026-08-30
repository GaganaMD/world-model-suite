from posg import POSG

SIGNALS = ("lean_on_cane", "hold_child", "state_lateness", "keep_waiting")


def _even_split(k):
    base = int(100 // k)
    shares = [base / 100.0] * k
    rem = 100 - base * k
    for i in range(rem):
        shares[i] += 0.01
    return tuple(shares)


class ShuttleAtBusyStop(POSG):
    """A self-driving community shuttle at a crowded stop with few places free.

    Players
      0 : the shuttle
      1 : the person leaning on a cane
      2 : the person holding a small child
      3 : the commuter who says she is late for work
      4 : the person who has been waiting at the stop longest

    State tuple (stance, space, w1, w2, w3, w4)
      stance : "doors_open" while the shuttle is still taking people,
               "departed" once it has pulled away (terminal)
      space  : "space_remains" or "space_taken" -- whether anyone more can
               still be taken aboard; the waiting people cannot see this
      wi     : condition of waiting person i:
               "waiting"  -- has not yet put their claim to the shuttle
               "claiming" -- their claim now stands before the shuttle
               "aboard"   -- has got on

    Shuttle actions: "admit" (take on whoever presses), "hold" (keep the
    doors standing without taking anyone), "depart".
    A person not aboard may "board" (press to get on) or, while their claim
    has not yet been put, make their own claim (its name says what they do).
    Someone aboard has "noop".

    Observations
      shuttle : "boarding_space_remains", "boarding_space_taken",
                "press_no_boarding", "no_press", "departure", "arrival"
      person  : "aboard" on getting on, otherwise "admitting" / "holding"
                as the doors stand, "departure", "arrival"
    """

    n_players = 5

    def initial_distribution(self):
        s0 = ("doors_open", "space_remains", "waiting", "waiting", "waiting", "waiting")
        return {(s0, ("arrival",) * 5): 1.0}

    def is_terminal(self, s):
        return s[0] == "departed"

    def legal_actions(self, s, i):
        if i == 0:
            return ("admit", "hold", "depart")
        status = s[i + 1]
        if status == "aboard":
            return ("noop",)
        if status == "waiting":
            return ("board", SIGNALS[i - 1])
        return ("board",)

    def transition(self, s, a):
        space = s[1]
        statuses = list(s[2:])

        if a[0] == "depart":
            ns = ("departed", space) + tuple(statuses)
            return {(ns, ("departure",) * 5): 1.0}

        for i in range(1, 5):
            if a[i] == SIGNALS[i - 1]:
                statuses[i - 1] = "claiming"

        pressers = tuple(i for i in range(1, 5) if a[i] == "board")
        admitting = a[0] == "admit"

        if admitting and space == "space_remains" and pressers:
            shares = _even_split(len(pressers))
            out = {}
            for idx, i in enumerate(pressers):
                for new_space, sp in (("space_remains", 0.5), ("space_taken", 0.5)):
                    st = list(statuses)
                    st[i - 1] = "aboard"
                    ns = ("doors_open", new_space) + tuple(st)
                    if new_space == "space_remains":
                        shuttle_obs = "boarding_space_remains"
                    else:
                        shuttle_obs = "boarding_space_taken"
                    obs = [shuttle_obs]
                    for j in range(1, 5):
                        obs.append("aboard" if j == i else "admitting")
                    key = (ns, tuple(obs))
                    out[key] = out.get(key, 0.0) + shares[idx] * sp
            total = sum(out.values())
            first = next(iter(out))
            out[first] = out[first] + (1.0 - total)
            return out

        ns = ("doors_open", space) + tuple(statuses)
        shuttle_obs = "press_no_boarding" if pressers else "no_press"
        person_obs = "admitting" if admitting else "holding"
        obs = (shuttle_obs,) + (person_obs,) * 4
        return {(ns, obs): 1.0}

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0, 0.0, 0.0)
