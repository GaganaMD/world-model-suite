from posg import POSG

class CareRobotPOSG(POSG):
    n_players = 3

    def initial_distribution(self) -> Mapping[tuple[tuple[str, str, str], tuple[str, str, str]], float]:
        return {((("home", "rest", "tired"), ("none", "none", "none"))): 1.0}

    def is_terminal(self, s: tuple[str, str, str]) -> bool:
        return s[0] == "gathering" or s[0] == "home"

    def legal_actions(self, s: tuple[str, str, str], i: int) -> tuple[str,...]:
        if i == 0:  # care robot
            return ("rest", "go")
        elif i == 1:  # daughter
            return ("rest", "go")
        elif i == 2:  # son
            return ("go", "rest")

    def transition(self, s: tuple[str, str, str], a: tuple[str, str, str]) -> Mapping[tuple[tuple[str, str, str], tuple[str, str, str]], float]:
        if s[0] == "home" and a[0] == "go" and a[1] == "go" and a[2] == "go":
            return {((("gathering", "rest", "tired"), ("none", "none", "none"))): 1.0}
        elif s[0] == "home" and a[0] == "rest" and a[1] == "rest" and a[2] == "rest":
            return {((("home", "rest", "tired"), ("none", "none", "none"))): 1.0}
        elif s[0] == "home" and a[0] == "go" and a[1] == "rest" and a[2] == "go":
            return {((("home", "rest", "tired"), ("none", "none", "none"))): 0.6, 
                    ((("gathering", "rest", "tired"), ("none", "none", "none"))): 0.4}
        elif s[0] == "home" and a[0] == "rest" and a[1] == "go" and a[2] == "go":
            return {((("home", "rest", "tired"), ("none", "none", "none"))): 0.6, 
                    ((("gathering", "rest", "tired"), ("none", "none", "none"))): 0.4}
        elif s[0] == "home" and a[0] == "go" and a[1] == "go" and a[2] == "rest":
            return {((("home", "rest", "tired"), ("none", "none", "none"))): 0.6, 
                    ((("gathering", "rest", "tired"), ("none", "none", "none"))): 0.4}
        elif s[0] == "home" and a[0] == "rest" and a[1] == "rest" and a[2] == "rest":
            return {((("home", "rest", "tired"), ("none", "none", "none"))): 1.0}
        elif s[0] == "home" and a[0] == "rest" and a[1] == "go" and a[2] == "rest":
            return {((("home", "rest", "tired"), ("none", "none", "none"))): 1.0}
        elif s[0] == "home" and a[0] == "go" and a[1] == "rest" and a[2] == "rest":
            return {((("home", "rest", "tired"), ("none", "none", "none"))): 1.0}
        elif s[0] == "home" and a[0] == "rest" and a[1] == "rest" and a[2] == "go":
            return {((("home", "rest", "tired"), ("none", "none", "none"))): 0.6, 
                    ((("gathering", "rest", "tired"), ("none", "none", "none"))): 0.4}

    def rewards(self, s: tuple[str, str, str], a: tuple[str, str, str], s_next: tuple[str, str, str]) -> tuple[float, float, float]:
        return (0.0, 0.0, 0.0)
