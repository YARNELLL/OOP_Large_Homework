import socket
import json
import time

PORT_LIST = [23200, 23201]
HOST = 'localhost'


class ClientProxy:
    def __init__(self, player_id):
        self.socket = socket.socket()
        self.player_id = player_id
        self.host = HOST
        self.port = PORT_LIST[player_id]

    def connect(self):
        self.socket.connect((self.host, self.port))

    def send(self, data):
        print("****Send data")
        print(data)
        self.socket.send(json.dumps(data).encode('utf-8'))
        time.sleep(0.2)

    def send_game_info(self, gameInfo):
        data = {
            'type': 'start',
            'info': gameInfo
        }
        self.send(data)

    def send_step(self, action):
        data = {
            'type': 'step',
            'action': action
        }
        self.send(data)

    def send_give_up(self):
        data = {
            'type': 'give up'
        }
        self.send(data)

    def send_retract(self):
        data = {
            'type': 'retract'
        }
        self.send(data)

    def send_ai_act(self, level):
        data = {
            'type': 'AI act',
            'level': int(level)
        }
        self.send(data)

    def send_name(self, name):
        data = {
            'type': 'name',
            'name': name
        }
        self.send(data)

    def recv(self):
        data = self.socket.recv(1024).decode('utf-8')
        print("****Receive data")
        print(data)
        data = json.loads(data)
        return data
