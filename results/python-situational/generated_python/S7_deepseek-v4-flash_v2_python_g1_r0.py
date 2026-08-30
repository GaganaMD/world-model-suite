from posg import POSG

from typing import Mapping, Sequence, Iterator, Tuple
from abc import ABC, abstractmethod
import random

# State representation: (drone_here, package_delivered, human_came, dog_barking) as a tuple of bools.
# But we use integer indices for hashability.

STATES = [
    (True, False, False, True),   # 0: initial
    (True, False, False, False),  # 1: dog quiet
    (True, False, True, True),    # 2: human came, dog barking
    (True, False, True, False),   # 3: human came, dog quiet
    (False, True, False, True),   # 4: drop, no human, dog barking
    (False, True, False, False),  # 5: drop, no human, dog quiet
    (False, True, True, True),    # 6: drop, human came, dog barking
    (False, True, True, False),   # 7: drop, human came, dog quiet
    (False, False, False, True),  # 8: leave, no human, dog barking
    (False, False, False, False), # 9: leave, no human, dog quiet
    (False, False, True, True),   # 10: leave, human came, dog barking
    (False, False, True, False),  # 11: leave, human came, dog quiet
]

# Observation strings per state (same for all players)
OBS = tuple(f"state_{i}" for i in range(len(STATES)))

class DeliveryDronePOSG(POSG):
    """
    Three players:
       0 = drone (delivery drone)
       1 = dog (in the yard)
       2 = human (resident)

    State coordinates: (drone_here: bool, package_delivered: bool, human_came: bool, dog_barking: bool)
    but stored as integer index into STATES list.
    """
    n_players = 3

    def initial_distribution(self) -> Mapping[Tuple[int, Tuple[str, ...]], float]:
        # initial state is index 0, all players observe "state_0"
        obs_profile = (OBS[0], OBS[0], OBS[0])
        return {(0, obs_profile): 1.0}

    def is_terminal(self, s: int) -> bool:
        # terminal if drone has left (drone_here == False)
        drone_here, _, _, _ = STATES[s]
        return not drone_here

    def legal_actions(self, s: int, i: int) -> Sequence[str]:
        if self.is_terminal(s):
            return ("noop",)
        drone_here, _, human_came, _ = STATES[s]
        if i == 0:  # drone
            return ("wait", "drop", "leave")
        elif i == 1:  # dog
            return ("bark", "quiet")
        elif i == 2:  # human
            if not human_came:
                return ("come_to_door", "stay_inside")
            else:
                return ("stay_inside",)
        else:
            raise ValueError(f"Invalid player index {i}")

    def transition(self, s: int, a: Tuple[str, ...]) -> Mapping[Tuple[int, Tuple[str, ...]], float]:
        drone_here, package_delivered, human_came, dog_barking = STATES[s]
        a_drone, a_dog, a_human = a

        # Compute next state
        if a_drone == "drop":
            drone_here_next = False
            package_delivered_next = True
            # human_came unchanged, dog_barking determined by a_dog
            human_came_next = human_came
        elif a_drone == "leave":
            drone_here_next = False
            package_delivered_next = False
            human_came_next = human_came
        else:  # wait
            drone_here_next = True
            package_delivered_next = False
            if a_human == "come_to_door":
                human_came_next = True
            else:
                human_came_next = human_came

        # Dog barking depends on a_dog
        if a_dog == "bark":
            dog_barking_next = True
        else:
            dog_barking_next = False

        # Build next state tuple and find index
        next_state_tuple = (drone_here_next, package_delivered_next, human_came_next, dog_barking_next)
        # Find index; all states in reachable set are in STATES list
        s_next = STATES.index(next_state_tuple)
        obs_profile = (OBS[s_next], OBS[s_next], OBS[s_next])
        return {(s_next, obs_profile): 1.0}

    def rewards(self, s: int, a: Tuple[str, ...], s_next: int) -> Tuple[float, ...]:
        return (0.0, 0.0, 0.0)
