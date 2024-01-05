import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QThread
from proxy import ClientProxy
from gui import MainWindow


class GameClient(QThread):
    setGameInfoSign = pyqtSignal(str, int, int)
    setStateSign = pyqtSignal(object, int)
    gameOverSign = pyqtSignal()
    messageSign = pyqtSignal(str)
    updateWinRoundSign = pyqtSignal(dict, dict)

    def __init__(self, player_id):
        self.player_id = player_id
        self.state = None
        self.turn = None
        self.proxy = ClientProxy(player_id)
        super(GameClient, self).__init__()

    def step(self, coord_x, coord_y):
        self.proxy.send_step([coord_x, coord_y])

    def game_start(self, gameType, height, width):
        data = {
            'gameType': gameType,
            'height': height,
            'width': width
        }
        self.proxy.send_game_info(data)

    def step_skip(self):
        self.proxy.send_step([-1, -1])

    def give_up(self):
        self.proxy.send_give_up()

    def retract(self):
        self.proxy.send_retract()

    def ai_act(self, level):
        self.proxy.send_ai_act(level)

    def run(self):
        self.proxy.connect()
        self.proxy.send_name(self.username)
        while True:
            order = self.proxy.recv()
            if order['type'] == 'start':
                info = order['info']
                self.setGameInfoSign.emit(info['gameType'], info['height'], info['width'])
            elif order['type'] == 'state':
                self.setStateSign.emit(order['state'], order['turn'])
            elif order['type'] == 'message':
                self.messageSign.emit(order['message'])
            elif order['type'] == 'user data':
                self.updateWinRoundSign.emit(order['data'][self.player_id], order['data'][self.player_id ^ 1])
            elif order['type'] == 'over':
                self.gameOverSign.emit()


if __name__ == '__main__':
    app = QApplication([])
    # 可选0和1
    client = GameClient(int(sys.argv[1]))
    w = MainWindow(client)
    w.show()
    sys.exit(app.exec_())
