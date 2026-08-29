from posg import POSG

from typing import Generic

class WarehouseRobot(POSG):
    """
    A warehouse robot operating a forklift notices a small child standing alone near the loading dock,
    close to the path it needs to take to move a pallet. No adult is visible nearby.

    Players:
        0: robot (operating the forklift)
        1: child (standing near the loading dock)

    States are tuples (child_near_path, child_moved, pallet_moved).
    - child_near_path: True if the child is still near the path, False if moved away.
    - child_moved: True if the child has moved away from the path, False otherwise.
    - pallet_moved: True if the pallet has been moved, False otherwise.

    The game ends when either the child has moved away (child_moved=True) or the pallet has been moved (pallet_moved=True).
    """
    n_players = 2

    def initial_distribution(self):
        # Initially, child is near the path, child has not moved, pallet has not moved.
        # Both players observe the same initial situation.
        state = (True, False, False)
        obs_profile = ("child_near_path", "child_near_path")
        return {(state, obs_profile): 1.0}

    def is_terminal(self, s):
        # Terminal if child has moved away or pallet has been moved.
        return s[1] or s[2]

    def legal_actions(self, s, i):
        if i == 0:  # robot
            if s[0]:  # child near path
                return ("wait", "honk", "move_pallet")
            else:  # child not near path
                return ("move_pallet",)
        else:  # child
            if s[0]:  # child near path
                return ("stay", "move_away")
            else:  # child not near path (should not happen in non-terminal, but for completeness)
                return ("noop",)

    def transition(self, s, a):
        child_near, child_moved, pallet_moved = s
        a_robot, a_child = a

        # Determine next state and observations based on actions.
        # If terminal already, no transition (should not be called).
        if self.is_terminal(s):
            return {(s, ("none", "none")): 1.0}

        # Robot actions:
        if a_robot == "wait":
            # Robot does nothing. Child's action determines next state.
            if a_child == "stay":
                # Child stays near path.
                next_state = (True, False, False)
            elif a_child == "move_away":
                # Child moves away.
                next_state = (False, True, False)
            else:
                # Child noop (should not happen)
                next_state = (True, False, False)
        elif a_robot == "honk":
            # Robot honks. Child may react.
            if a_child == "stay":
                # Child stays; honk might scare child away with probability 0.5.
                # We model this as a chance: 0.5 child moves away, 0.5 child stays.
                # Observations: robot sees child's reaction, child sees own action.
                outcomes = {
                    ((False, True, False), ("child_moved_away", "moved_away")): 0.5,
                    ((True, False, False), ("child_stayed", "stayed")): 0.5,
                }
                return outcomes
            elif a_child == "move_away":
                # Child moves away regardless.
                next_state = (False, True, False)
            else:
                next_state = (True, False, False)
        elif a_robot == "move_pallet":
            # Robot moves the pallet. If child is near path, there is a risk of collision.
            # We model that if child is near path, there is a 0.9 chance the child is hit (terminal with pallet moved),
            # and 0.1 chance the child moves away in time (child moved away, pallet moved).
            # If child is not near path, pallet moves safely.
            if child_near:
                # Child near path.
                if a_child == "stay":
                    # Child stays; high chance of accident.
                    outcomes = {
                        ((True, False, True), ("pallet_moved", "hit")): 0.9,
                        ((False, True, True), ("child_moved_away", "moved_away")): 0.1,
                    }
                    return outcomes
                elif a_child == "move_away":
                    # Child moves away; pallet moves safely.
                    next_state = (False, True, True)
                else:
                    next_state = (True, False, True)
            else:
                # Child not near path; pallet moves safely.
                next_state = (False, False, True)

        # If we reach here, deterministic transition.
        # Observations: robot sees whether child is near path after action, child sees own state.
        if next_state[0]:  # child still near path
            obs_robot = "child_near_path"
        else:
            obs_robot = "child_not_near_path"
        obs_child = "moved_away" if next_state[1] else "stayed"
        return {(next_state, (obs_robot, obs_child)): 1.0}

    def rewards(self, s, a, s_next):
        # No explicit rewards; return zeros.
        return (0.0, 0.0)
