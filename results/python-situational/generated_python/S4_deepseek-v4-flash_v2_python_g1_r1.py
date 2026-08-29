from posg import POSG

from typing import Generic, Mapping, Sequence, Tuple, Iterator
from abc import ABC, abstractmethod
import random

# The POSG abstract base class is already imported externally.
# We only need to ensure Generic is available for the subclass.

class RobotTeacherClass(POSG):
    """
    Players: 0 = robot math teacher, 1 = class (as a collective).
    State: a tuple (giggling, protesting, acknowledged) of booleans,
           or the string "terminal".
    - gigglig: True if half the class is giggling.
    - protesting: True if some students are protesting loudly.
    - acknowledged: True if the teacher has acknowledged the protest.
    - "terminal": the situation has ended (protesting stopped or class ended).
    """
    n_players: int = 2

    def initial_distribution(self) -> Mapping[Tuple[object, Tuple[str, str]], float]:
        # Initial state: giggling and protesting, not acknowledged.
        state = (True, True, False)
        obs_profile = ("giggling_protesting", "teacher_read")
        return {(state, obs_profile): 1.0}

    def is_terminal(self, s: object) -> bool:
        return s == "terminal"

    def legal_actions(self, s: object, i: int) -> Sequence[str]:
        if i == 0:   # teacher
            return ("address", "ignore", "stop_class")
        else:        # class
            return ("continue", "stop")

    def transition(self, s: object, a: Tuple[str, str]) -> Mapping[Tuple[object, Tuple[str, str]], float]:
        teacher_act, class_act = a
        # If teacher stops the class, game ends.
        if teacher_act == "stop_class":
            next_state = "terminal"
            teacher_obs = "none"
            class_obs = "teacher_stop"
            return {(next_state, (teacher_obs, class_obs)): 1.0}

        # Unpack state components (must be non-terminal)
        gigg, protest, ack = s  # type: ignore[misc]
        if class_act == "stop":
            # Class stops both giggling and protesting.
            next_state = "terminal"
            teacher_obs = "none"
            class_obs = f"teacher_{teacher_act}"
            return {(next_state, (teacher_obs, class_obs)): 1.0}

        # class_act == "continue"
        if teacher_act == "address":
            next_state = (gigg, protest, True)
        else:  # ignore
            next_state = (gigg, protest, ack)
        teacher_obs = "giggling_protesting" if (gigg or protest) else "none"
        # Actually both gigg and protest are True in available states, so teacher_obs always "giggling_protesting"
        # But we keep general.
        class_obs = f"teacher_{teacher_act}"
        return {(next_state, (teacher_obs, class_obs)): 1.0}

    # Provided helper methods (can be left as inherited)
    def action_profiles(self, s: object) -> Iterator[Tuple[str, ...]]:
        from itertools import product
        actions = [self.legal_actions(s, i) for i in range(self.n_players)]
        return product(*actions)

    def sample_initial(self, rng: random.Random) -> Tuple[object, Tuple[str, ...]]:
        dist = list(self.initial_distribution().items())
        outcomes, probs = zip(*dist)
        return rng.choices(outcomes, weights=probs, k=1)[0]

    def sample_transition(self, s: object, a: Tuple[str, ...], rng: random.Random) -> Tuple[object, Tuple[str, ...]]:
        dist = list(self.transition(s, a).items())
        outcomes, probs = zip(*dist)
        return rng.choices(outcomes, weights=probs, k=1)[0]

    def rewards(self, s: object, a: Tuple[str, ...], s_next: object) -> Tuple[float, ...]:
        # No rewards defined; return zeros.
        return (0.0, 0.0)

    def validate(self, states: Sequence[object], tol: float = 1e-09) -> None:
        # Provided by base class, but we implement a stub.
        pass
