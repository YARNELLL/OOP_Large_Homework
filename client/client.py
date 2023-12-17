import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import pyqtSignal, QThread
from proxy import ClientProxy
from gui import MainWindow


class GameClient(QThread):
    def __init__(self, player_id):
        self.player_id = player_id
        self.state = None
        self.turn = None
        self.proxy = ClientProxy(player_id)

        self.setGameInfoSign = pyqtSignal(str, int, int)
        self.setStateSign = pyqtSignal(object, int)
        self.gameOverSign = pyqtSignal()
        self.messageSign = pyqtSignal(str)
        super(GameClient, self).__init__()

    def step(self, coord_x, coord_y):
        self.proxy.sendStep([coord_x, coord_y])

    def gameStart(self, gameType, height, width):
        data = {
            'gameType': gameType,
            'height': height,
            'width': width
        }
        self.proxy.sendGameInfo(data)

    def stepSkip(self):
        self.proxy.sendStep([-1, -1])

    def giveUp(self):
        self.proxy.sendGiveup()

    def retract(self):
        self.proxy.sendRetract()

    def run(self):
        self.proxy.connect()
        while True:
            order = self.proxy.recv()
            if order['type'] == 'start':
                info = order['info']
                self.setGameInfoSign.emit(info['gameType'], info['height'], info['width'])
            elif order['type'] == 'state':
                self.setStateSign.emit(order['state'], order['turn'])
            elif order['type'] == 'message':
                self.messageSign.emit(order['message'])
            elif order['type'] == 'over':
                self.gameOverSign.emit()


if __name__ == '__main__':
    app = QApplication([])

    client = GameClient(int(sys.argv[1]))
    w = MainWindow(client)
    w.show()
    client.start()
    sys.exit(app.exec_())
