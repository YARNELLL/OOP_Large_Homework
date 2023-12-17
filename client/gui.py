from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMainWindow, QWidget, QListView, QPushButton, QComboBox, QGridLayout, QHBoxLayout, \
    QVBoxLayout, QLineEdit, QLabel, QMessageBox


class QLabelCenter(QLabel):
    def __init__(self, text=''):
        super().__init__(text)
        self.setAlignment(Qt.AlignCenter)


class MyEdit(QWidget):
    def __init__(self, label, text):
        super().__init__()

        h_layout = QHBoxLayout()
        self.setLayout(h_layout)

        self.label = QLabelCenter(label)
        self.edit = QLineEdit(text)
        h_layout.addWidget(self.label, 1)
        h_layout.addWidget(self.edit, 3)


class Grid(QWidget):
    pushSign = pyqtSignal(int, int)

    def __init__(self, parent, coord_x, coord_y, grid_size):
        super().__init__(parent)
        self.coord_x = coord_x
        self.coord_y = coord_y
        self.grid_size = grid_size

        self.setFixedSize(grid_size, grid_size)

        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.layout)

        self.label = QLabelCenter()
        self.layout.addWidget(self.label)
        self.set_state(-1)

    def set_state(self, state):
        grid_pix = QPixmap('./img/grid.png')
        white_piece_pix = QPixmap('./img/white_piece.png')
        black_piece_pix = QPixmap('./img/black_piece.png')
        if state == -1:
            pix = grid_pix
        elif state == 0:
            pix = black_piece_pix
        elif state == 1:
            pix = white_piece_pix
        else:
            raise ValueError('Invalid state type {}'.format(state))

        self.label.setPixmap(pix.scaled(self.grid_size, self.grid_size))

    def mousePressEvent(self, QMouseEvent):
        self.pushSign.emit(self.coord_x, self.coord_y)


class Chessboard(QWidget):
    def __init__(self, parent, client):
        super().__init__(parent)
        self.width = None
        self.height = None
        self.client = client
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.setLayout(self.grid_layout)
        self.myGrid = {}
        self.setAttribute(Qt.WA_StyledBackground, True)

    def reset(self, height, width):
        for i in range(self.grid_layout.count()):
            self.grid_layout.itemAt(i).widget().deleteLater()
        self.myGrid = {}

        self.height = height
        self.width = width
        grid_size = 50
        # print("width:{},height:{}".format(width, height))
        self.setFixedSize(grid_size * width, grid_size * height)

        for i in range(height):
            for j in range(width):
                gird = Grid(self, i, j, grid_size)
                gird.pushSign.connect(self.client.step)
                self.grid_layout.addWidget(gird, *(i, j))
                self.myGrid[(i, j)] = gird

    def set_state(self, state):
        for i in range(self.height):
            for j in range(self.width):
                self.myGrid[(i, j)].set_state(state[i][j])


class Menu(QWidget):
    gameStartSign = pyqtSignal(str, int, int)
    stepSkipSign = pyqtSignal()
    giveUpSign = pyqtSignal()

    def __init__(self, parent, client):
        super().__init__(parent)
        self.giveUpButton = None
        self.retractButton = None
        self.skipButton = None
        self.startButton = None
        self.gameTypeBox = None
        self.heightEdit = None
        self.widthEdit = None
        self.hintLabel = None
        self.client = client
        self.init_ui()

    def init_ui(self):
        v_layout = QVBoxLayout()
        self.setLayout(v_layout)

        self.hintLabel = QLabelCenter('Wait for start.')
        self.widthEdit = MyEdit('Width', '8')
        self.heightEdit = MyEdit('Height', '8')
        self.gameTypeBox = QComboBox(self)
        self.gameTypeBox.setView(QListView())
        self.gameTypeBox.addItem("Gobang")
        self.gameTypeBox.addItem("Go")
        self.gameTypeBox.addItem("Reversi")
        self.startButton = QPushButton('start')
        self.startButton.clicked.connect(self.game_start)
        self.skipButton = QPushButton('Skip')
        self.skipButton.clicked.connect(self.step_skip)
        self.retractButton = QPushButton('Retract')
        self.retractButton.clicked.connect(self.retract)
        self.giveUpButton = QPushButton('Give up')
        self.giveUpButton.clicked.connect(self.give_up)

        v_layout.addWidget(self.hintLabel)
        v_layout.addWidget(self.widthEdit)
        v_layout.addWidget(self.heightEdit)
        v_layout.addWidget(self.gameTypeBox)
        v_layout.addWidget(self.startButton)
        v_layout.addWidget(self.skipButton)
        v_layout.addWidget(self.retractButton)
        v_layout.addWidget(self.giveUpButton)

    def game_start(self):
        game_type = self.gameTypeBox.currentText()
        height = int(self.heightEdit.edit.text())
        width = int(self.widthEdit.edit.text())
        self.client.game_start(game_type, height, width)

    def step_skip(self):
        self.client.step_skip()

    def give_up(self):
        self.client.give_up()

    def retract(self):
        self.client.retract()


class MainWindow(QMainWindow):
    def __init__(self, client):
        super().__init__()
        self.menu = None
        self.board = None
        self.client = client
        self.client.setGameInfoSign.connect(self.set_game_info)
        self.client.setStateSign.connect(self.set_state)
        self.client.messageSign.connect(self.show_message)
        self.client.gameOverSign.connect(self.game_over)
        self.init_ui()

    def init_ui(self):
        main_widget = QWidget(self)
        h_layout = QHBoxLayout()
        main_widget.setLayout(h_layout)
        self.board = Chessboard(main_widget, self.client)
        self.board.reset(8, 8)
        self.menu = Menu(main_widget, self.client)
        h_layout.addWidget(self.board)
        h_layout.addWidget(self.menu)

        self.setCentralWidget(main_widget)
        file = open('./client.qss', 'r')
        self.setStyleSheet(file.read())

    def set_game_info(self, game_type, height, width):
        # game_type虽然没有用，但是不能删除，因为传入的参数有三个，去掉game_type会导致参数对应出问题
        # print(game_type, height, width)
        self.board.reset(height, width)

    def set_state(self, state, turn):
        self.board.set_state(state)
        if turn == self.client.player_id:
            self.menu.hintLabel.setText('Your turn.')
        else:
            self.menu.hintLabel.setText('Wait for the opponent.')

    def show_message(self, message):
        QMessageBox.warning(self, 'Message', message)

    def game_over(self):
        self.menu.hintLabel.setText('Wait for start.')
