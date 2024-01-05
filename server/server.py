from proxy import ServerProxy
from rule import create_rule, MementoBox
from ai import create_ai
from userData import user_data


class GameServer:
    def __init__(self) -> None:
        self.proxy = ServerProxy()
        pass

    def game_loop(self):
        memory = MementoBox()
        game_info, first_player_id = self.proxy.send_game_start()

        rule = create_rule(game_info['gameType'], game_info['height'], game_info['width'])
        rule.reset()
        rule.turn = first_player_id
        data = rule.store()
        memory.store(*data)
        self.proxy.send_state(data[0], data[1])
        while True:
            player_id, data = self.proxy.recv()

            if data['type'] == 'AI act':
                AI = create_ai(data['level'], rule)
                data = {
                    'type': 'step',
                    'action': AI.act(),
                }

            if data['type'] == 'step':
                action = {
                    'coord': data['action'],
                    'player_id': player_id
                }
                valid, message = rule.step(action)
                if valid:
                    memory.store(rule.state, rule.turn)
                    finish, winner = rule.judge_finish()
                    self.proxy.send_state(rule.state, rule.turn)
                    if finish:
                        break
                else:
                    self.proxy.send_message(message, player_id)
            elif data['type'] == 'retract':
                successful, data = memory.retract(player_id)
                rule.restore(*data)
                self.proxy.send_state(rule.state, rule.turn)
                if successful:
                    self.proxy.send_message("Retract successfully.", player_id)
                else:
                    self.proxy.send_message("Retract error.", player_id)
            elif data['type'] == 'give up':
                winner = player_id ^ 1
                break
            elif data['type'] == 'start':
                self.proxy.send_message('Please finish this game.', player_id)
            else:
                raise ValueError('Invalid action type {}'.format(data['type']))

        self.proxy.send_game_over(winner)
        self.proxy.send_message('Game over. Winner is {}'.format(self.user_name[winner]))
        result = {
            'winner': winner,
            'exit': False
        }
        if winner > -1 and self.user_name[winner]:
            user_data.win(self.user_name[winner])

        return result

    def main_loop(self):
        self.user_name = self.proxy.connect()

        while True:
            self.proxy.send_user_data([user_data.get(self.user_name[0]), user_data.get(self.user_name[1])])
            result = self.game_loop()
            print('Game over', result)
            if result['exit']:
                break
        self.proxy.close()


if __name__ == "__main__":
    game = GameServer()
    game.main_loop()
