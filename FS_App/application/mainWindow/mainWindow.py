from os import path
from dataModel import ModelDatabase 
from inputOutput import AbaqusReader
from visualization import Viewport, InteractionStyles
from application.terminal import Terminal
from application.mainWindow.mainWindowShell import MainWindowShell
from PySide6.QtWidgets import QFileDialog

class MainWindow(MainWindowShell):
    '''
    The main window.
    '''

    @property
    def terminal(self) -> Terminal:
        '''The Python terminal.'''
        return self._terminal

    @property
    def viewport(self) -> Viewport:
        '''The visualization viewport.'''
        return self._viewport

    # attribute slots
    __slots__ = ('_modelDatabase',)

    def __init__(self) -> None:
        '''Main window constructor.'''
        super().__init__()
        # model database
        self._modelDatabase: ModelDatabase | None = None
        # setup connections
        self._menuBarFileNew.triggered.connect(self.onMenuBarFileNew) # type: ignore

    def show(self) -> None:
        '''
        Shows the widget and its child widgets.
        Initializes the viewport.
        '''
        super().show()
        self._viewport.initialize(InteractionStyles.Rotate)

    def setModelDatabase(self, filePath: str) -> None:
        '''
        Creates a model database from file.
        Updates the GUI based on the new model database.
        '''
        # create model database from file
        extension: str = path.splitext(filePath)[1]
        match extension:
            case '.inp': self._modelDatabase = AbaqusReader.read(filePath)
            case _: raise ValueError(f"invalid file extension: '{extension}'")
        # update model tree and viewport
        self._modelTree.setModelDatabase(self._modelDatabase)
        self._viewport.setMesh(self._modelDatabase.mesh)

#-----------------------------------------------------------------------------------------------------------------------
# Menu Bar
#-----------------------------------------------------------------------------------------------------------------------

    def onMenuBarFileNew(self) -> None:
        '''On Menu Bar > File > New.'''
        filePath: str = QFileDialog.getOpenFileName( # type: ignore
            parent=self,
            caption='Open Mesh Input File',
            filter='Abaqus Input Files (*.inp);;All Files (*.*)',
            options=QFileDialog.Option.DontUseNativeDialog
        )[0]
        if filePath != '': self.setModelDatabase(filePath)
