from visualization import InteractionStyles
from application.terminal import Terminal
from application.mainWindow.mainWindowShell import MainWindowShell

class MainWindow(MainWindowShell):
    '''
    The main window.
    '''

    @property
    def terminal(self) -> Terminal:
        '''The Python terminal.'''
        return self._terminal

    # attribute slots
    __slots__ = ()

    def __init__(self) -> None:
        '''Main window constructor.'''
        super().__init__()

    def show(self) -> None:
        '''
        Shows the widget and its child widgets.
        Initializes the viewport.
        '''
        super().show()
        self._viewport.initialize(InteractionStyles.Rotate)
