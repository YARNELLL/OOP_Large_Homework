from proxy import ServerProxy
from rule import create, MementoBox


class GameServer:
    def __init__(self) -> None:
        self.proxy = ServerProxy()
        pass

    def game_loop(self):
        memory = MementoBox()
        game_info = self.proxy.send_game_start()
        rule = create(game_info['gameType'], game_info['height'], game_info['width'])
        rule.reset()
        memory.store(*rule.store())
        self.proxy.send_state(*rule.store())
        while True:
            player_id, data = self.proxy.recv()
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
        self.proxy.send_message('Game over. Winner is player {}'.format(winner))
        result = {
            'winner': winner,
            'exit': False
        }
        return result

    def main_loop(self):
        self.proxy.connect()
        while True:
            result = self.game_loop()
            print('Game over', result)
            if result['exit']:
                break
        self.proxy.close()


if __name__ == "__main__":
    game = GameServer()
    print('Server started.')
    game.main_loop()
