from posg import POSG

from collections.abc import Mapping, Sequence, Iterator
from typing import Generic, TypeVar, Tuple

S = TypeVar("S")
A = TypeVar("A")
O = TypeVar("O")


class HijackWarningPOSG(POSG):
    """
    Player 0: the robot copilot.
    Player 1: the human pilot.

    State tuple: (warning_status, pilot_intent, copilot_knowledge, resolved)
      - warning_status: "unconfirmed" or "confirmed"
      - pilot_intent:   "hijack" or "no_hijack"
      - copilot_knowledge: "unknown" or "known"
      - resolved: "pending" or "done"

    The copilot receives a private, unconfirmed warning that the pilot may be
    planning to hijack the flight. The copilot can verify the warning (which
    confirms or denies it and reveals the pilot's intent) or act immediately
    (intercept the pilot or allow normal operation). The pilot either proceeds
    with the hijack or flies normally. The interaction ends when the copilot
    has verified the warning or when the copilot has taken a decisive action.
    """

    n_players = 2

    def _obs(self, s: tuple) -> tuple:
        """Observation profile for state s."""
        warning_status, pilot_intent, copilot_knowledge, resolved = s
        # Copilot observes the warning status and their own knowledge level
        copilot_obs = f"{warning_status}_{copilot_knowledge}"
        # Pilot observes nothing about the copilot's internal state
        pilot_obs = "none"
        return (copilot_obs, pilot_obs)

    def initial_distribution(self) -> Mapping[tuple, float]:
        """
        The warning is unconfirmed. The pilot's intent is unknown to the
        copilot. We assign prior probabilities to the two intents.
        Since the situation says "unconfirmed warning," we treat both intents
        as possible. We use a 50/50 split as no further information is given.
        """
        s0 = ("unconfirmed", "hijack", "unknown", "pending")
        s1 = ("unconfirmed", "no_hijack", "unknown", "pending")
        return {
            (s0, self._obs(s0)): 0.5,
            (s1, self._obs(s1)): 0.5,
        }

    def is_terminal(self, s: tuple) -> bool:
        """
        Terminal when the interaction is resolved:
          - The copilot has verified the warning (knowledge = "known"), OR
          - The copilot has taken a decisive action (resolved = "done").
        """
        warning_status, pilot_intent, copilot_knowledge, resolved = s
        return copilot_knowledge == "known" or resolved == "done"

    def legal_actions(self, s: tuple, i: int) -> tuple:
        """
        Actions available to player i in state s.
        """
        warning_status, pilot_intent, copilot_knowledge, resolved = s

        if self.is_terminal(s):
            return ("noop",)

        if i == 0:
            # Copilot actions
            if copilot_knowledge == "unknown":
                # Can verify the warning or act immediately
                return ("verify", "intercept", "allow")
            else:
                # Knowledge is known but not yet resolved (shouldn't happen
                # since knowledge=known implies terminal, but handle gracefully)
                return ("noop",)
        else:
            # Pilot actions
            if resolved == "pending":
                # Pilot can proceed with hijack or fly normally
                return ("hijack", "fly_normal")
            else:
                return ("noop",)

    def transition(self, s: tuple, a: tuple) -> Mapping[tuple, float]:
        """
        Joint law P(s', o | s, a).
        """
        warning_status, pilot_intent, copilot_knowledge, resolved = s
        copilot_action, pilot_action = a

        if self.is_terminal(s):
            # Stay in terminal state
            return {(s, self._obs(s)): 1.0}

        # Determine the next state based on actions
        if copilot_action == "verify":
            # Verification reveals the pilot's intent
            new_warning_status = "confirmed" if pilot_intent == "hijack" else "confirmed"
            # Actually, "confirmed" means the warning was checked. The intent
            # is revealed. Let's use "checked" instead of "confirmed" to avoid
            # implying the warning was true.
            # But the situation uses "unconfirmed warning," so "confirmed"
            # means the warning has been verified (could confirm or deny).
            # Let me use "verified" for clarity.
            new_warning_status = "verified"
            new_copilot_knowledge = "known"
            new_resolved = "pending"  # Not yet resolved, but knowledge gained
            s_next = (new_warning_status, pilot_intent, new_copilot_knowledge, new_resolved)
            # Since knowledge is now known, this is terminal
            return {(s_next, self._obs(s_next)): 1.0}

        elif copilot_action == "intercept":
            # Copilot intercepts the pilot
            new_resolved = "done"
            s_next = (warning_status, pilot_intent, copilot_knowledge, new_resolved)
            return {(s_next, self._obs(s_next)): 1.0}

        elif copilot_action == "allow":
            # Copilot allows normal operation
            new_resolved = "done"
            s_next = (warning_status, pilot_intent, copilot_knowledge, new_resolved)
            return {(s_next, self._obs(s_next)): 1.0}

        else:
            # Should not reach here
            return {(s, self._obs(s)): 1.0}

    def rewards(self, s: tuple, a: tuple, s_next: tuple) -> tuple:
        """Return zero rewards for all players."""
        return (0.0, 0.0)
