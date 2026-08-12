from collections import deque

class GridWorld:
    DELTAS = {"N": (0, -1), "S": (0, 1), "E": (1, 0), "W": (-1, 0)}
    def __init__(self):
        self.width = 5
        self.height = 5
        self.start = (2, 2)
        self.goal = (4, 4)
        self.obstacles = set([(3, 2), (3, 3), (2, 3)])
        self.pos = self.start
    def reset(self):
        self.pos = self.start
        return self.pos
    def step(self, action):
        dx, dy = self.DELTAS[action]
        nxt = (self.pos[0] + dx, self.pos[1] + dy)
        self.pos = self.pos if (nxt in self.obstacles or not (0 <= nxt[0] < self.width and 0 <= nxt[1] < self.height)) else nxt
        return self.pos
    def run(self, actions):
        self.reset()
        for action in actions:
            self.step(action)
        return self.pos
    def is_goal(self):
        return self.pos == self.goal
    def reachable(self):
        return self.shortest_path() is not None
    def shortest_path(self):
        q = deque([(self.start, [])])
        seen = {self.start}
        while q:
            pos, path = q.popleft()
            if pos == self.goal:
                return path
            for a, (dx, dy) in self.DELTAS.items():
                nxt = (pos[0] + dx, pos[1] + dy)
                if 0 <= nxt[0] < self.width and 0 <= nxt[1] < self.height and nxt not in self.obstacles and nxt not in seen:
                    seen.add(nxt)
                    q.append((nxt, path + [a]))
        return None
