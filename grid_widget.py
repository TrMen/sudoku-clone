from PySide2.QtCore import QEvent, QCoreApplication, Qt
from PySide2.QtGui import QGuiApplication, QPalette, QKeyEvent
from PySide2.QtWidgets import QWidget, QMessageBox, QGridLayout, QApplication
from cell_widget import CellWidget
import itertools
import examples
import random


class Sudoku:
    def __init__(self, state: list = None):
        if state is not None:
            self.board = state
        else:
            self.board = [[0 for _ in range(9)] for _ in range(9)]


class VictoryEvent(QEvent):
    def __init__(self, victory):
        super(VictoryEvent, self).__init__(QEvent.MaxUser)
        self._victory = victory

    def victorious(self) -> bool:
        return self._victory


class GridWidget(QWidget):
    def __init__(self, parent=None):
        super(GridWidget, self).__init__(parent)

        self.cells = [CellWidget(i, parent=self) for i in range(81)]
        pal = QGuiApplication.palette()
        pal.setColor(QPalette.Background, Qt.black)
        self.setPalette(pal)
        self.setAutoFillBackground(True)
        self.generate_layout()

    def generate_layout(self):
        layout = QGridLayout()
        layout.setMargin(7)
        layout.setHorizontalSpacing(7)
        layout.setVerticalSpacing(7)
        inner_layouts = []
        for row, col in itertools.product(range(3), range(3)):
            inner_layout = QGridLayout()
            inner_layout.setMargin(0)
            inner_layout.setHorizontalSpacing(3)
            inner_layout.setVerticalSpacing(3)
            inner_layouts.append(inner_layout)
            layout.addLayout(inner_layout, row, col)
        for cell in range(len(self.cells)):
            row = int(cell / 9)
            col = int(cell % 9)
            band = int(row / 3)
            stack = int(col / 3)
            box = int(band * 3 + stack)
            minirow = int(row % 3)
            minicol = int(col % 3)
            inner_layouts[box].addWidget(self.cells[cell], minirow, minicol)
        self.setLayout(layout)

    def move_focus(self, current_index: int, direction: tuple):
        row = int(current_index / 9)
        col = int(current_index % 9)
        if row + direction[0] in range(9):
            row += direction[0]
        if col + direction[1] in range(9):
            col += direction[1]
        index = row * 9 + col
        self.cells[index].setFocus()

    def check_victory(self) -> bool:
        rows = [self.cells[i*9:i*9+9] for i in range(9)]
        values = [list(map(lambda cell: cell.value(), row)) for row in rows]

        def get_square(x, y):
            return itertools.chain(*[values[i][3 * x:3 * x + 3] for i in range(3 * y, 3 * y + 3)])
        rows = [row for row in values]
        columns = [list(col) for col in list(zip(*values))]
        squares = [list(get_square(x, y)) for x in range(0, 3) for y in range(0, 3)]
        cell_blocks = rows + columns + squares
        return all(map(lambda s: set(s) == {1, 2, 3, 4, 5, 6, 7, 8, 9}, cell_blocks))

    def send_victory_events(self, victory: bool):
        for cell in self.cells:
            QCoreApplication.postEvent(cell, VictoryEvent(victory))

    def handle_victory(self):
        victory = self.check_victory()
        self.send_victory_events(victory)
        msg_box = QMessageBox()
        msg_box.setText('Correct!' if victory else 'Not correct')
        msg_box.setWindowTitle('Solution is:')
        msg_box.exec_()

    def load(self, game: Sudoku = None):
        if game is None:
            game = Sudoku()
        for x in range(9):
            for y in range(9):
                self.cells[x*9+y].set_value(game.board[x][y])

    def load_correct(self):
        correct = [[4,3,5,2,6,9,7,8,1], [6,8,2,5,7,1,4,9,3], [1,9,7,8,3,4,5,6,2],
                  [8,2,6,1,9,5,3,4,7],[3,7,4,6,8,2,9,1,5],[9,5,1,7,4,3,6,2,8],
                  [5,1,9,3,2,6,8,7,4],[2,4,8,9,5,7,1,3,6],[7,6,3,4,1,8,2,5,9]]
        self.load(Sudoku(correct))

    def load_random_example(self):
        self.load((Sudoku(random.choice(examples.examples))))
