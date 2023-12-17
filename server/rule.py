from copy import deepcopy
import numpy as np
import queue

# 定义四个方向
DIRECTION_4 = np.array([[0, 1], [1, 0], [0, -1], [-1, 0]])
DIRECTION_8 = np.array([[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]])


class MementoBox:
    def __init__(self) -> None:
        self.memento = []

    def store(self, state, turn):
        self.memento.append((deepcopy(state), turn))

    def retract(self, player_id):
        if len(self.memento) < 2:
            return False, self.memento[-1]
        if player_id == self.memento[-2][1]:
            del self.memento[-1]
            return True, self.memento[-1]

        if len(self.memento) < 3:
            return False, self.memento[-1]
        del self.memento[-2:]
        return True, self.memento[-1]


class BaseRule:
    def __init__(self, height, width) -> None:
        self.height = height
        self.width = width
        self.shape = (self.height, self.width)
        self.state = None
        self.turn = 0
        pass

    def reset(self):
        self.state = (np.zeros(self.shape) - 1).tolist()
        self.turn = 0

    def valid_coordinate(self, coord):
        if any(coord < 0) or any(coord >= self.shape):
            return False
        return True

    def valid_action(self, action):
        coord, player_id = np.array(action['coord']), action['player_id']
        return self.valid_coordinate(coord)

    def step(self, action):
        if not self.valid_action(action):
            return False, "Invalid action"
        return True, "Successfully"

    def judge_finish(self):
        state = self.state
        assert (np.min(state) >= -1)
        assert (np.max(state) <= 2)

        win = [False, False]
        space_count = 0

        for direction in DIRECTION_8[:4]:
            count = np.zeros(self.shape, dtype=np.uint8)
            for x in range(self.height):
                for y in range(self.width):
                    if state[x][y] == -1:
                        space_count += 1
                        continue
                    last_pos = np.array([x, y]) - direction
                    if self.valid_coordinate(last_pos) and state[x][y] == state[last_pos[0]][last_pos[1]]:
                        count[x][y] = count[last_pos[0]][last_pos[1]] + 1
                        if count[x][y] == 5:
                            win[state[x][y]] = True
                    else:
                        count[x][y] = 1

        if all(win):
            return True, -1
        for p in [0, 1]:
            if win[p]:
                return True, p
        if space_count == 0:
            return True, -1
        return False, None

    def restore(self, state, turn):
        self.state = state
        self.turn = turn

    def store(self):
        return self.state, self.turn


class GobangRule(BaseRule):
    def valid_action(self, action):
        if not super().valid_action(action):
            return False
        coord, player_id = action['coord'], action['player_id']
        if not self.state[coord[0]][coord[1]] == -1:
            return False
        return True

    def step(self, action):
        if not self.valid_action(action):
            return False, "Invalid action"

        coord, player_id = action['coord'], action['player_id']
        if player_id != self.turn:
            return False, "Not the turn of player {}".format(player_id)

        self.state[coord[0]][coord[1]] = player_id
        self.turn ^= 1
        return True, "Successfully"


class GoRule(BaseRule):
    def __init__(self, height, width):
        super().__init__(height, width)
        self.qi = None

    def calc_qi(self, state):
        qi = np.zeros(self.shape)
        belong = np.zeros(self.shape, dtype=np.int8) - 1
        block_num = 0
        block_qi = []
        # bfs
        for x in range(self.height):
            for y in range(self.width):
                if belong[x][y] == -1 and state[x][y] != -1:
                    belong[x][y] = block_num
                    block_qi.append(0)
                    q = queue.Queue()
                    q.put(np.array((x, y)))
                    while not q.empty():
                        now = q.get()
                        for direction in DIRECTION_4:
                            next_position = now + direction
                            if (self.valid_coordinate(next_position) and
                                    belong[next_position[0]][next_position[1]] == -1):
                                if state[next_position[0]][next_position[1]] == state[x][y]:
                                    belong[next_position[0]][next_position[1]] = block_num
                                    q.put(next_position)
                                elif state[next_position[0]][next_position[1]] == -1:
                                    block_qi[-1] += 1
                    block_num += 1
                if state[x][y] != -1:
                    qi[x][y] = block_qi[belong[x][y]]
        return qi

    def valid_action(self, action):
        if not super().valid_action(action):
            return False
        coord, player_id = action['coord'], action['player_id']
        if not self.state[coord[0]][coord[1]] == -1:
            return False
        self.state[coord[0]][coord[1]] = player_id
        self.qi = self.calc_qi(self.state)
        self.state[coord[0]][coord[1]] = -1
        if self.qi[coord[0]][coord[1]] == 0:
            remove = False
            for direction in DIRECTION_4:
                next_position = coord + direction
                if self.valid_coordinate(next_position) and self.state[next_position[0]][next_position[1]] == (
                        player_id ^ 1) and self.qi[next_position[0]][next_position[1]] == 0:
                    remove = True
            if not remove:
                return False
        return True

    def step(self, action):
        coord, player_id = action['coord'], action['player_id']
        if player_id != self.turn:
            return False, "Not the turn of player {}".format(player_id)

        if action['coord'][0] == -1:
            self.turn ^= 1
            return True, "Successfully"

        if not self.valid_action(action):
            return False, "Invalid action"

        self.state[coord[0]][coord[1]] = player_id
        self.turn ^= 1
        for x in range(self.height):
            for y in range(self.width):
                if self.state[x][y] == (player_id ^ 1) and self.qi[x][y] == 0:
                    self.state[x][y] = -1
        return True, "Successfully"


# 工厂方法，根据输入的gameType类型，返回不同的游戏规则
def create(gameType, *argv):
    # print("Game type is {}".format(gameType))
    if gameType == 'Gobang':
        return GobangRule(*argv)
    elif gameType == 'Go':
        return GoRule(*argv)
    else:
        raise ValueError("Invalid product name.")
