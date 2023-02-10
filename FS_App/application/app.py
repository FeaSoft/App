import sys
from application.mainWindow import MainWindow
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QLocale

QLocale.setDefault(QLocale.c())

class App(QApplication):
    '''
    The main application object.
    '''

    @property
    def mainWindow(self) -> MainWindow:
        '''The main window of the application.'''
        return self._mainWindow

    # attribute slots
    __slots__ = ('_isRunning', '_mainWindow')

    def __init__(self, argv: list[str]) -> None:
        '''App constructor.'''
        super().__init__(argv)
        super().setStyle('Fusion')
        self._isRunning: bool = False
        self._mainWindow: MainWindow = MainWindow()

    def start(self) -> int:
        '''
        Starts the application.
        Returns the exit code.
        '''
        if self._isRunning:
            raise RuntimeError('the application event loop has already been started')
        self._isRunning = True
        self._mainWindow.show()
        return self.exec()

current: App = App(sys.argv)
