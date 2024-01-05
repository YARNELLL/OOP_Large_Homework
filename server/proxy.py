import socket
import json
import sys
import time

sys.path.append('./..')
import settings


class ServerProxy:
    def __init__(self) -> None:
        pass

    def connect(self):
        socket.setdefaulttimeout(0.2)
        self.socket = [socket.socket(), socket.socket()]
        self.client = [None] * 2
        host = settings.HOST
        for s, port in zip(self.socket, settings.PORT_LIST):
            s.bind((host, port))
            s.listen(5)

        connected = [False, False]
        username = [None, None]
        while not all(connected):
            for i in range(2):
                if not connected[i]:
                    try:
                        self.client[i], add = self.socket[i].accept()
                        username[i] = self.recv([i])[1]['name']
                    except socket.timeout:
                        continue
                    print('****Player {} connected.'.format(i))
                    connected[i] = True
        return username

    def send(self, data, player_id=[0, 1]):
        if not (type(player_id) == list):
            player_id = [player_id]

        for p in player_id:
            self.client[p].send(json.dumps(data).encode('utf-8'))

        print("****Send data to {}".format(player_id))
        print(data)
        time.sleep(0.2)

    def sendGameStart(self):
        while True:
            player_id, action = self.recv()
            if action['type'] == 'start':
                break
            self.sendMessage('Game not start.', player_id)
        game_info = action['info']

        game_info_message = {
            'type': 'start',
            'info': game_info
        }
        self.send(game_info_message)
        self.sendMessage('{} game start.'.format(game_info['gameType']))

        return game_info, player_id

    def sendGameOver(self, winner):
        over_order = {
            'type': 'over',
            'winner': winner
        }
        self.send(over_order)

    def sendState(self, state, turn):
        data = {
            'type': 'state',
            'state': state,
            'turn': turn
        }
        self.send(data)

    def sendMessage(self, message, player_id=[0, 1]):
        data = {
            'type': 'message',
            'message': message
        }
        self.send(data, player_id)

    def sendUserData(self, data):
        data = {
            'type': 'user data',
            'data': data
        }
        self.send(data)

    def recv(self, id=[0, 1]):
        while True:
            for player_id in id:
                try:
                    data = json.loads(self.client[player_id].recv(1024).decode('utf-8'))
                except socket.timeout:
                    continue

                print("****Receive data from {}".format(player_id))
                print(data)
                return player_id, data

    def close(self):
        for s in self.socket:
            s.close()
