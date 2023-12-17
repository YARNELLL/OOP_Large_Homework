import socket
import json
import sys
import settings

sys.path.append('..')


class ClientProxy:
    def __init__(self, player_id):
        self.socket = socket.socket()
        self.player_id = player_id
        self.host = settings.HOST
        self.port = settings.PORT_LIST[player_id]

    def connect(self):
        self.socket.connect((self.host, self.port))

    def send(self, data):
        print("****Send data")
        print(data)
        self.socket.send(json.dumps(data).encode('utf-8'))

    def sendGameInfo(self, gameInfo):
        data = {
            'type': 'start',
            'info': gameInfo
        }
        self.send(data)

    def sendStep(self, action):
        data = {
            'type': 'step',
            'action': action
        }
        self.send(data)

    def sendGiveup(self):
        data = {
            'type': 'give up'
        }
        self.send(data)

    def sendRetract(self):
        data = {
            'type': 'retract'
        }
        self.send(data)

    def recv(self):
        data = self.socket.recv(1024).decode('utf-8')
        data = json.loads(data)
        print("****Receive data")
        print(data)
        return data
