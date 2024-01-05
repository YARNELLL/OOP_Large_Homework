from proxy import ServerProxy
import time
from rule import RuleFactory, MementoBox
from ai import AIFactory
from userData import user_data

class GameServer:
    def __init__(self) -> None:
        self.proxy = ServerProxy()
        pass
    
    def gameLoop(self):
        memory = MementoBox()
        gameInfo, first_player_id = self.proxy.sendGameStart()
                
        rule = RuleFactory.create(gameInfo['gameType'], gameInfo['height'], gameInfo['width'])
        rule.reset()
        rule.turn = first_player_id
        data = rule.store()
        memory.store(*data)
        self.proxy.sendState(data[0], data[1])
        while True:
            player_id, data = self.proxy.recv()
            
            if data['type'] == 'AI act':
                AI = AIFactory.create(data['level'], rule)
                data = {
                    'type': 'step',
                    'action': AI.act(),
                }
            
            if data['type'] == 'step':
                action = {
                    'coord': data['action'],
                    'player_id': player_id
                }
                vaild, message = rule.step(action)
                if vaild:
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
                winner = player_id^1
                break
            elif data['type'] == 'start':
                self.proxy.sendMessage('Please finish this game.', player_id)
            else:
                raise ValueError('Invaild action type {}'.format(data['type']))
            
        self.proxy.sendGameOver(winner)
        self.proxy.sendMessage('Game over. Winner is {}'.format(self.user_name[winner]))
        result = {
            'winner': winner,
            'exit': False
        }
        if winner > -1 and self.user_name[winner]:
            user_data.win(self.user_name[winner])
            
        return result
        
    
    def mainLoop(self):
        self.user_name = self.proxy.connect()
        
        while True:
            self.proxy.sendUserData([user_data.get(self.user_name[0]), user_data.get(self.user_name[1])])
            result = self.gameLoop()
            print('Game over', result)
            if result['exit']:
                break
        self.proxy.close()
    
if __name__ == "__main__":
    game = GameServer()
    game.mainLoop()