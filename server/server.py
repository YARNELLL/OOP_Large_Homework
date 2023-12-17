from proxy import ServerProxy
from rule import create, MementoBox


class GameServer:
    def __init__(self) -> None:
        self.proxy = ServerProxy()
        pass

    def gameLoop(self):
        memory = MementoBox()
        gameInfo = self.proxy.sendGameStart()
        rule = create(gameInfo['height'], gameInfo['width'])
        rule.reset()
        memory.store(*rule.store())
        self.proxy.sendState(*rule.store())
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
                    finish, winner = rule.judgeFinish()
                    self.proxy.sendState(rule.state, rule.turn)
                    if finish:
                        break
                else:
                    self.proxy.sendMessage(message, player_id)
            elif data['type'] == 'retract':
                successful, data = memory.retract(player_id)
                rule.restore(*data)
                self.proxy.sendState(rule.state, rule.turn)
                if successful:
                    self.proxy.sendMessage("Retract successfully.", player_id)
                else:
                    self.proxy.sendMessage("Retract error.", player_id)
            elif data['type'] == 'give up':
                winner = player_id ^ 1
                break
            elif data['type'] == 'start':
                self.proxy.sendMessage('Please finish this game.', player_id)
            else:
                raise ValueError('Invalid action type {}'.format(data['type']))

        self.proxy.sendGameOver(winner)
        self.proxy.sendMessage('Game over. Winner is player {}'.format(winner))
        result = {
            'winner': winner,
            'exit': False
        }
        return result

    def mainLoop(self):
        self.proxy.connect()
        while True:
            result = self.gameLoop()
            print('Game over', result)
            if result['exit']:
                break
        self.proxy.close()


if __name__ == "__main__":
    game = GameServer()
    game.mainLoop()
