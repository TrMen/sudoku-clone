from PySide2.QtGui import QKeyEvent, QPaintEvent, QPainter, QColor, QBrush, QFontDatabase, QFocusEvent
from PySide2.QtWidgets import QWidget, QSizePolicy, QFrame
from PySide2.QtCore import Qt, QEvent


class CellState:
    def __init__(self):
        self.digit = 0
        self.last_digit = 0
        self.mode = 'display'


class CellWidget(QFrame):
    _bg_display = QColor(255, 255, 255)  # White
    _bg_entry = QColor(0, 191, 255)  # deepskyblue
    _fg_color = QColor(0, 0, 0)  # Black
    _bg_victory = QColor(50, 205, 50)  # limegreen

    def __init__(self, index: int, parent=None):
        super(CellWidget, self).__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFocusPolicy(Qt.ClickFocus)
        self._state = CellState()
        self._index = index
        self._grid = parent

    def value(self) -> int:
        return self._state.digit

    def set_value(self, value: int):
        self._state.last_digit = self._state.digit
        self._state.digit = value
        self.update()

    def keyPressEvent(self, event: QKeyEvent):
        if self._state.mode == 'display':
            return

        if event.key() in range(Qt.Key_0, Qt.Key_9+1):
            self.set_value(event.key() - Qt.Key_0)

        if event.key() == Qt.Key_Backspace:
            self._state.digit = self._state.last_digit

        directions = {Qt.Key_Up: (-1, 0), Qt.Key_Down: (1, 0), Qt.Key_Left: (0, -1), Qt.Key_Right: (0, 1)}
        if event.key() in directions.keys():
            self._grid.move_focus(self._index, directions[event.key()])

        self.update()

    def focusInEvent(self, event: QFocusEvent):
        self._state.mode = 'entry'
        self.update()

    def focusOutEvent(self, event: QFocusEvent):
        self._state.mode = 'display'
        self.update()

    def paintEvent(self, event: QPaintEvent):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        # Draw background
        painter.setBrush(QBrush(self.bg()))
        painter.drawRect(event.rect())

        # Draw digit
        font = QFontDatabase.systemFont(QFontDatabase.FixedFont)
        font.setPixelSize(int(self.width() * 6/7))
        digit = str(self._state.digit) if self._state.digit != 0 else ' '
        painter.setPen(self._fg_color)
        painter.setFont(font)
        flags = Qt.AlignCenter | Qt.TextJustificationForced
        painter.drawText(event.rect(), flags, digit)

    def bg(self):
        if self._state.mode == 'display':
            return self._bg_display
        elif self._state.mode == 'victory':
            return self._bg_victory
        return self._bg_entry

    def event(self, event: QEvent) -> bool:
        if event.type() == QEvent.MaxUser:
            self._state.mode = 'victory' if event.victorious() else 'display'
            return True
        return QWidget.event(self, event)
