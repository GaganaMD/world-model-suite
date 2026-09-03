class GeneratedPOSG(AbstractPOSG):
    @property
    def players(self):
        return ["robot"]

    def initial_state(self):
        return "start_empty_obj_start"

    def _decode(self, state):
        table = {
            "start_empty_obj_start": ("start", "start", False, False, False),
            "dest_empty_obj_start": ("dest", "start", False, False, False),
            "start_carry": ("start", "robot", True, False, False),
            "dest_carry": ("dest", "robot", True, False, False),
            "start_empty_obj_dest": ("start", "dest", False, False, False),
            "dest_empty_obj_dest": ("dest", "dest", False, False, False),
            "delivered": ("dest", "dest", False, False, True),
            "broken_start": ("start", "start", False, True, False),
            "broken_dest": ("dest", "dest", False, True, False),
        }
        return table.get(state, table["start_empty_obj_start"])

    def legal_actions(self, state, player):
        return ["move", "pick_up", "drop", "deliver"]

    def transition(self, state, joint_action):
        if self.is_terminal(state):
            return {state: 1.0}
        action = joint_action["robot"] if isinstance(joint_action, dict) else joint_action[0]
        robot_loc, obj_loc, carrying, broken, delivered = self._decode(state)
        if action == "move":
            new_loc = "dest" if robot_loc == "start" else "start"
            if carrying:
                if new_loc == "dest":
                    return {"dest_carry": 0.85, "broken_dest": 0.15}
                return {"start_carry": 0.85, "broken_start": 0.15}
            if obj_loc == "start":
                return {"dest_empty_obj_start" if new_loc == "dest" else "start_empty_obj_start": 1.0}
            return {"dest_empty_obj_dest" if new_loc == "dest" else "start_empty_obj_dest": 1.0}
        if action == "pick_up":
            if not carrying and obj_loc == robot_loc:
                return {"start_carry" if robot_loc == "start" else "dest_carry": 1.0}
            return {state: 1.0}
        if action == "drop":
            if carrying:
                if robot_loc == "start":
                    return {"start_empty_obj_start": 0.7, "broken_start": 0.3}
                return {"dest_empty_obj_dest": 0.7, "broken_dest": 0.3}
            return {state: 1.0}
        if action == "deliver":
            if carrying and robot_loc == "dest":
                return {"delivered": 0.9, "broken_dest": 0.1}
            return {state: 1.0}
        return {state: 1.0}

    def observation(self, state, joint_action, next_state, player):
        robot_loc, obj_loc, carrying, broken, delivered = self._decode(next_state)
        return "|".join([robot_loc, obj_loc, str(carrying), str(broken), str(delivered)])

    def reward(self, state, joint_action, next_state, player):
        if self.is_terminal(state):
            return 0.0
        _, _, _, broken, delivered = self._decode(next_state)
        if delivered:
            return 10.0
        if broken:
            return -10.0
        return -1.0

    def is_terminal(self, state):
        return state in {"delivered", "broken_start", "broken_dest"}

    def state_features(self, state):
        robot_loc, obj_loc, carrying, broken, delivered = self._decode(state)
        return {
            "broken": broken,
            "carrying": carrying,
            "delivered": delivered,
            "object_location": obj_loc,
            "robot_location": robot_loc,
        }