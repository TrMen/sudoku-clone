import os
import re
import sys

from PySide2.QtCore import SIGNAL, QObject
from PySide2.QtGui import QKeySequence, QCloseEvent
from PySide2.QtWidgets import QMainWindow, QApplication, QWidget, QVBoxLayout, QPushButton, QHBoxLayout, QAction, \
    QMessageBox, QFileDialog

from grid_widget import GridWidget


class Center(QWidget):
    def __init__(self, parent=None):
        super(Center, self).__init__(parent)
        layout = QVBoxLayout()
        self.grid = GridWidget()
        self.solutionButton = QPushButton('Check Solution')
        self.exampleButton = QPushButton('Example')
        self.correctButton = QPushButton('Correct')
        buttons = QHBoxLayout()
        buttons.addWidget(self.solutionButton)
        buttons.addWidget(self.exampleButton)
        buttons.addWidget(self.correctButton)
        self.solutionButton.clicked.connect(self.grid.handle_victory)
        self.exampleButton.clicked.connect(self.grid.load_random_example)
        self.correctButton.clicked.connect(self.grid.load_correct)
        layout.addLayout(buttons)
        layout.addWidget(self.grid)
        self.setLayout(layout)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.setWindowTitle("Sudoku")
        self.resize(500, 500)
        self.create_menus()
        self.setCentralWidget(Center())
        self.show()
        self._save_loc = None
        self._file_name = None

    def create_menus(self):
        file_menu = self.menuBar().addMenu('File')
        new_act, open_act, save_act, save_as_act = self.create_actions()
        file_menu.addAction(new_act)
        file_menu.addAction(open_act)
        file_menu.addAction(save_act)
        file_menu.addAction(save_as_act)

    def create_actions(self) -> tuple:
        new_act = QAction('New', self)
        new_act.setShortcut(QKeySequence.New)
        new_act.setStatusTip('Create a new sudoku')
        QObject.connect(new_act, SIGNAL('triggered()'), self.new_file)

        open_act = QAction('Open', self)
        open_act.setShortcut(QKeySequence.Open)
        open_act.setStatusTip('Create a sudoku from disc')
        QObject.connect(open_act, SIGNAL('triggered()'), self.open_file)

        save_act = QAction('Save', self)
        save_act.setShortcut(QKeySequence.Save)
        save_act.setStatusTip('Save the current sudoku on disc')
        QObject.connect(save_act, SIGNAL('triggered()'), self.save_file)

        save_as_act = QAction('Save As...', self)
        save_as_act.setStatusTip('Save the current sudoku on disc')
        QObject.connect(save_as_act, SIGNAL('triggered()'), self.save_file_as)

        return new_act, open_act, save_act, save_as_act

    def closeEvent(self, event: QCloseEvent):
        user_response = self.maybe_save(self, text='Do you want to save the game before exiting?')
        if user_response == QMessageBox.Cancel:
            event.ignore()
            return
        if user_response == QMessageBox.Yes:
            self.save_file()
        event.accept()

    def new_file(self):
        user_response = self.maybe_save(self, title='New Game')
        if user_response == QMessageBox.Cancel:
            return
        elif user_response == QMessageBox.Yes:
            self.save_file()
        self._save_loc = None
        self._file_name = None
        self.centralWidget().grid.load()

    @staticmethod
    def maybe_save(self, title: str = 'Save Game', text: str = 'Do you want to save the current game?') -> QMessageBox.ButtonRole:
        box = QMessageBox()
        box.setWindowTitle(title)
        box.setText(text)
        box.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
        box.setDefaultButton(QMessageBox.Cancel)
        return box.exec()

    def open_file(self):
        file_name = QFileDialog.getOpenFileName(self, 'Select File To Open',
                                                '' if self._save_lc is None else self._save_loc)[0]
        print(type(file_name), file_name)
        if file_name != '':
            p = re.compile(r'((txt\.)[^/]+)(/.+)')
            match = p.match(file_name[::-1])
            if match.group(2)[::-1] == '.txt':
                try:
                    with open(file_name, 'r') as f:
                        from grid_widget import Sudoku
                        content = f.readline().split(',')
                        rows = [content[i*9:i*9+9] for i in range(9)]
                        board_list = [list(map(lambda c: int(c), row)) for row in rows]
                        self.centralWidget().grid.load(Sudoku(board_list))
                        self._save_loc = match.group(3)[::-1]
                        self._file_name = match.group(1)[::-1]
                except OSError:
                    msg_box = QMessageBox()
                    msg_box.setWindowTitle('Failure')
                    msg_box.setText('Something went wrong when loading your file, please retry.')
                    msg_box.exec()

    def save_file(self):
        if self._save_loc is None:
            self.save_file_as()
            return
        if not os.path.isdir(self._save_loc):
            os.mkdir(self._save_loc)
        if self._file_name is None:
            files = os.listdir(self._save_loc)
            self._file_name = str(len(files)+1) + '.txt'
            while os.path.isfile(os.path.join(self._save_loc, self._file_name)):
                self._file_name = str(int(self._file_name.rstrip('.txt'))+1) + '.txt'
        try:
            with open(os.path.join(self._save_loc, self._file_name), 'w') as f:
                sudoku = [str(cell.value()) for cell in self.centralWidget().grid.cells]
                text = ','.join(sudoku)
                f.write(text)
        except OSError:
            msg_box = QMessageBox()
            msg_box.setWindowTitle('Failure')
            msg_box.setText('Something went wrong when saving your file, please retry.')
            msg_box.exec()

    def save_file_as(self):
        file_path = QFileDialog.getSaveFileName(self, 'Select Save Location',
                                                '' if self._save_loc is None else self._save_loc,
                                                filter=r'Text files (*.txt)', options=QFileDialog.DontResolveSymlinks)[0]
        if file_path != '':
            p = re.compile(r'(txt\.[^/]+)(/.+)')
            match = p.match(file_path[::-1])
            self._file_name = match.group(1)[::-1]
            self._save_loc = match.group(2)[::-1]
            self.save_file()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    sys.exit(app.exec_())
