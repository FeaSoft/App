from typing import cast
from collections.abc import Callable
from code import InteractiveConsole
from PySide6.QtWidgets import QWidget, QTextEdit, QLineEdit, QVBoxLayout
from PySide6.QtCore import QObject, QEvent
from PySide6.QtGui import Qt, QFont, QKeyEvent, QTextCursor

class Terminal(QWidget):
    '''
    An interactive Python terminal.
    '''

    class OutputRedirect:
        '''
        Class for redirecting standard output streams.
        '''

        # attribute slots
        __slots__ = ('_onWrite', '_textColor')

        def __init__(self, onWrite: Callable[[str, str], None], textColor: str) -> None:
            '''Output redirect constructor.'''
            self._onWrite: Callable[[str, str], None] = onWrite
            self._textColor: str = textColor

        def write(self, text: str) -> None:
            '''On write.'''
            text = text.strip()
            if text != '': self._onWrite(text, self._textColor)

    class InputRedirect:
        '''
        Class for redirecting standard input streams.
        '''

        # attribute slots
        __slots__ = ()

        def readline(self) -> None:
            '''On read line.'''
            raise RuntimeError('standard input is not allowed')

    @property
    def stdout(self) -> OutputRedirect:
        '''Exposes the stdout stream redirector.'''
        return self._stdout

    @property
    def stderr(self) -> OutputRedirect:
        '''Exposes the stderr stream redirector.'''
        return self._stderr

    @property
    def stdin(self) -> InputRedirect:
        '''Exposes the stdin stream redirector.'''
        return self._stdin

    # attribute slots
    __slots__ = (
        '_layout', '_outputBox', '_inputBox', '_interpreter', '_history', '_historyIndex', '_stdout', '_stderr',
        '_stdin'
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        '''Terminal constructor.'''
        super().__init__(parent)
        # font
        font: QFont = QFont('Courier', 9)
        # layout
        self._layout: QVBoxLayout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self._layout)
        # output box
        self._outputBox: QTextEdit = QTextEdit(self)
        self._outputBox.setFont(font)
        self._outputBox.setCursor(Qt.CursorShape.IBeamCursor)
        self._outputBox.setReadOnly(True)
        self._layout.addWidget(self._outputBox)
        # input box
        self._inputBox: QLineEdit = QLineEdit(self)
        self._inputBox.setFont(font)
        self._inputBox.setCursor(Qt.CursorShape.IBeamCursor)
        self._inputBox.setReadOnly(False)
        self._inputBox.installEventFilter(self)
        self._layout.addWidget(self._inputBox)
        # interpreter & interpreter history
        self._interpreter: InteractiveConsole = InteractiveConsole(locals={})
        self._history: list[str] = ['']
        self._historyIndex: int = 0
        # streams
        self._stdout: Terminal.OutputRedirect = Terminal.OutputRedirect(self.print, 'black')
        self._stderr: Terminal.OutputRedirect = Terminal.OutputRedirect(self.print, 'red')
        self._stdin: Terminal.InputRedirect = Terminal.InputRedirect()

    def eventFilter(self, watched: QObject, event: QEvent) -> bool:
        '''The event filter.'''
        if watched == self._inputBox and event.type() == QEvent.Type.KeyPress:
            keyEvent: QKeyEvent = cast(QKeyEvent, event)
            match keyEvent.key():
                case Qt.Key.Key_Return:
                    source = self._inputBox.text()
                    self._inputBox.clear()
                    self.interpret(source)
                case Qt.Key.Key_Up:
                    self._inputBox.setText(self.getPreviousInput(True))
                case Qt.Key.Key_Down:
                    self._inputBox.setText(self.getPreviousInput(False))
                case _:
                    pass
        return False # allow further event processing

    def getPreviousInput(self, moveBackward: bool) -> str:
        '''Navigate user input history.'''
        # update history index
        if moveBackward: self._historyIndex -= 1
        else: self._historyIndex += 1
        # fix out of bounds
        if self._historyIndex >= len(self._history): self._historyIndex = len(self._history) - 1
        elif self._historyIndex < 0: self._historyIndex = 0
        # return the next or previous user input in the list
        return self._history[self._historyIndex]

    def print(self, text: str, color: str = 'black') -> None:
        '''Prints the received text to the output box.'''
        # deselect any text (required)
        textCursor: QTextCursor = self._outputBox.textCursor()
        textCursor.clearSelection()
        textCursor.movePosition(QTextCursor.MoveOperation.End)
        self._outputBox.setTextCursor(textCursor)
        # print with color
        self._outputBox.setTextColor(color)
        self._outputBox.append(text)
        self._outputBox.ensureCursorVisible()

    def interpret(self, source: str, print: bool = True) -> None:
        '''Interprets and prints the received Python source string.'''
        if print:
            self._history[-1] = source
            self._history.append('')
            self._historyIndex = len(self._history) - 1
            self.print('>>> ' + source, 'blue')
        self._interpreter.push(source)
