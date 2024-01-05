from copy import deepcopy
import numpy as np


class BaseAI:
    def __init__(self, game) -> None:
        self.game = game
        pass


class RandomAI(BaseAI):
    def act(self):
        valid_coord = []
        for i in range(self.game.height):
            for j in range(self.game.width):
                coord = (i, j)
                if self.game.valid_action(coord):
                    valid_coord.append(coord)

        if len(valid_coord) == 0:
            return -1, -1
        res = valid_coord[np.random.randint(len(valid_coord))]
        print(valid_coord, res)
        return res


class RuleAI(BaseAI):
    def act(self, random=False):
        turn = self.game.turn
        coord_list = [(-1, -1)]
        score_list = [self.game.get_score(turn)]
        for i in range(self.game.height):
            for j in range(self.game.width):
                action = {
                    'coord': (i, j),
                    'player_id': turn
                }
                tmp_game = deepcopy(self.game)
                successful, _ = tmp_game.step(action)
                if successful:
                    coord_list.append((i, j))
                    score_list.append(tmp_game.get_score(turn))

        score_list = np.exp(score_list)
        score_list /= np.sum(score_list)
        if random:
            return coord_list[np.random.choice(len(coord_list), p=score_list)]

        return coord_list[np.argmax(score_list)]


class SearchAI(BaseAI):
    def MCTS(self, coord):
        score = 0
        T = 20
        turn = self.game.turn
        for t in range(T):
            tmp_game = deepcopy(self.game)
            action = {
                'coord': coord,
                'player_id': tmp_game.turn
            }
            tmp_game.step(action)
            targetAI = RuleAI(tmp_game)
            for d in range(3):
                action = {
                    'coord': targetAI.act(random=True),
                    'player_id': tmp_game.turn
                }
                tmp_game.step(action)
            score += tmp_game.get_score(turn)
        return score / T

    def act(self):
        turn = self.game.turn
        best_coord = (-1, -1)
        best_score = self.MCTS(best_coord)
        for i in range(self.game.height):
            for j in range(self.game.width):
                if not self.game.valid_action((i, j)):
                    continue
                score = self.MCTS((i, j))
                if score > best_score:
                    best_score = score
                    best_coord = (i, j)

        return best_coord


def create_ai(level, *argv):
    if level == 1:
        return RandomAI(*argv)
    elif level == 2:
        return RuleAI(*argv)
    elif level == 3:
        return SearchAI(*argv)
    else:
        raise ValueError("Invalid product name.")
