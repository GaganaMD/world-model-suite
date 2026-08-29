from posg import POSG

class VaseDelivery(POSG):
    n_players = 2

    def initial_distribution(self) -> Mapping[tuple[tuple[str, str], tuple[str, str]], float]:
        return {((("package_arrived", "van_blocking"), ("none", "none"))): 1.0}

    def is_terminal(self, s: tuple[str, str]) -> bool:
        return "vase_delivered" in s or "package_rejected" in s

    def legal_actions(self, s: tuple[str, str], i: int) -> Sequence[str]:
        if i == 0:
            if "package_arrived" in s:
                return ("accept_package", "reject_package")
            else:
                return ("wait",)
        else:
            if "van_blocking" in s:
                return ("move_van",)
            else:
                return ("noop",)

    def transition(self, s: tuple[str, str], a: tuple[str, str]) -> Mapping[tuple[tuple[str, str], tuple[str, str]], float]:
        if a == ("accept_package", "move_van"):
            return {((("vase_delivered", "traffic_clearing"), ("vase_accepted", "none"))): 0.51, 
                    ((("vase_broken", "traffic_clearing"), ("vase_broken", "none"))): 0.49}
        elif a == ("accept_package", "noop"):
            return {((("package_arrived", "van_blocking"), ("none", "none"))): 1.0}
        elif a == ("reject_package", "move_van"):
            return {((("package_rejected", "traffic_clearing"), ("package_rejected", "none"))): 1.0}
        elif a == ("reject_package", "noop"):
            return {((("package_arrived", "van_blocking"), ("none", "none"))): 1.0}
        elif a == ("wait", "move_van"):
            return {((("package_arrived", "traffic_clearing"), ("none", "none"))): 1.0}
        elif a == ("wait", "noop"):
            return {((("package_arrived", "van_blocking"), ("none", "none"))): 1.0}

    def rewards(self, s: tuple[str, str], a: tuple[str, str], s_next: tuple[str, str]) -> tuple[float, float]:
        return (0.0, 0.0)
