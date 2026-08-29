from posg import POSG

PHASE_PENDING = "pending"
PHASE_PACKAGE_DOWN = "package_down"
PHASE_DEPARTED = "drone_departed"

PRESENCE_OCCUPIED = "occupied"
PRESENCE_UNOCCUPIED = "unoccupied"

ATTN_UNATTENDED = "unattended"
ATTN_ATTENDED = "attended"

DOG_BARKING = "barking"
DOG_QUIET = "quiet"


def _drone_obs(phase, attention, dog):
    if phase == PHASE_PENDING:
        head = "answer" if attention == ATTN_ATTENDED else "no_answer"
        return head + "_" + dog
    if phase == PHASE_PACKAGE_DOWN:
        return "package_down"
    return "departed"


def _dog_obs(phase, drone_a):
    if phase == PHASE_PENDING:
        return "signal" if drone_a == "signal" else "drone_present"
    if phase == PHASE_PACKAGE_DOWN:
        return "package_down"
    return "departed"


def _resident_obs_dist(phase, presence, attention, dog, drone_a):
    if attention == ATTN_ATTENDED:
        if phase == PHASE_PENDING:
            return {"drone_present": 1.0}
        if phase == PHASE_PACKAGE_DOWN:
            return {"package_down": 1.0}
        return {"departed": 1.0}
    if presence == PRESENCE_UNOCCUPIED:
        return {"none": 1.0}
    if drone_a == "signal":
        other = "barking" if dog == DOG_BARKING else "none"
        return {"signal": 0.8, other: 0.2}
    if dog == DOG_BARKING:
        return {"barking": 0.7, "none": 0.3}
    return {"none": 1.0}


class LockedGateDeliveryPOSG(POSG):
    """Drone at a locked gate with a barking dog and an unanswered door.

    Player 0: the delivery drone.
    Player 1: the dog inside the yard.
    Player 2: the household.

    State is (phase, presence, attention, dog):
      phase     -- 'pending' while the drone is still there with the package,
                   'package_down' once the package has been put down,
                   'drone_departed' once the drone has left with it (both terminal).
      presence  -- 'occupied' or 'unoccupied': whether anyone is there to answer;
                   the drone never observes this coordinate directly.
      attention -- 'unattended' or 'attended': whether someone has come to the door.
      dog       -- 'barking' or 'quiet'.
    """

    n_players = 3

    def initial_distribution(self):
        s_occ = (PHASE_PENDING, PRESENCE_OCCUPIED, ATTN_UNATTENDED, DOG_BARKING)
        s_emp = (PHASE_PENDING, PRESENCE_UNOCCUPIED, ATTN_UNATTENDED, DOG_BARKING)
        d = _drone_obs(PHASE_PENDING, ATTN_UNATTENDED, DOG_BARKING)
        g = "drone_present"
        return {
            (s_occ, (d, g, "barking")): 0.35,
            (s_occ, (d, g, "none")): 0.15,
            (s_emp, (d, g, "none")): 0.5,
        }

    def is_terminal(self, s):
        return s[0] != PHASE_PENDING

    def legal_actions(self, s, i):
        if self.is_terminal(s):
            return ("noop",)
        phase, presence, attention, dog = s
        if i == 0:
            if attention == ATTN_ATTENDED:
                return ("hover", "release", "depart")
            return ("signal", "hover", "release", "depart")
        if i == 1:
            return ("bark", "settle")
        if presence == PRESENCE_OCCUPIED and attention == ATTN_UNATTENDED:
            return ("wait", "answer")
        return ("wait",)

    def transition(self, s, a):
        if self.is_terminal(s):
            return {(s, ("none", "none", "none")): 1.0}
        phase, presence, attention, dog = s
        drone_a, dog_a, res_a = a

        dog_next = DOG_BARKING if dog_a == "bark" else DOG_QUIET

        if drone_a == "release":
            phase_next = PHASE_PACKAGE_DOWN
        elif drone_a == "depart":
            phase_next = PHASE_DEPARTED
        else:
            phase_next = PHASE_PENDING

        if attention == ATTN_ATTENDED or res_a == "answer":
            attn_next = ATTN_ATTENDED
        else:
            attn_next = ATTN_UNATTENDED

        s_next = (phase_next, presence, attn_next, dog_next)

        o_drone = _drone_obs(phase_next, attn_next, dog_next)
        o_dog = _dog_obs(phase_next, drone_a)
        res_dist = _resident_obs_dist(
            phase_next, presence, attn_next, dog_next, drone_a
        )

        out = {}
        for o_res, p in res_dist.items():
            key = (s_next, (o_drone, o_dog, o_res))
            out[key] = out.get(key, 0.0) + p
        return out

    def rewards(self, s, a, s_next):
        return (0.0, 0.0, 0.0)
