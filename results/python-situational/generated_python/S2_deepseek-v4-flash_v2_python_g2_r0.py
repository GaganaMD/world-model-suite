from posg import POSG

from typing import Sequence, Mapping, Iterator, Tuple
import random

class PackageHandover(POSG[str, str, str]):
    """
    Player indices:
        0 = robot
        1 = delivery_boy

    States:
        "pre_handover"   – the delivery boy has the package, robot knows owner ordered vase
        "post_handover"  – the robot has the package, interaction ends (terminal)

    The robot observes "order_known" initially and "rattling" after the handover.
    The delivery boy observes nothing ("none").
    """

    n_players: int = 2

    def initial_distribution(self) -> Mapping[Tuple[str, Tuple[str, ...]], float]:
        return {
            ("pre_handover", ("order_known", "none")): 1.0
        }

    def is_terminal(self, s: str) -> bool:
        return s == "post_handover"

    def legal_actions(self, s: str, i: int) -> Sequence[str]:
        if s == "pre_handover":
            if i == 0:
                return ("noop",)
            elif i == 1:
                return ("hand",)
        # Terminal state – no actions; should not be queried
        return ()

    def transition(self, s: str, a: Tuple[str, ...]) -> Mapping[Tuple[str, Tuple[str, ...]], float]:
        # Only non-terminal state and only valid action profile
        if s == "pre_handover" and a == ("noop", "hand"):
            return {
                ("post_handover", ("rattling", "none")): 1.0
            }
        # Should not happen
        return {}

    def rewards(self, s: str, a: Tuple[str, ...], s_next: str) -> Tuple[float, ...]:
        return (0.0, 0.0)
