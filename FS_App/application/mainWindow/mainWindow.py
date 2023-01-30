from os import path
from dataModel import ModelingSpaces, DataObject, NodeSet, ElementSet, ModelDatabase
from inputOutput import AbaqusReader
from visualization import Viewport, Views, InteractionStyles
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
        self._modelTree.currentItemChanged.connect(self.onModelTreeSelection)     # type: ignore
        self._menuBarFileNew.triggered.connect(self.onMenuBarFileNew)             # type: ignore
        self._toolBarFileNew.triggered.connect(self.onToolBarFileNew)             # type: ignore
        self._toolBarViewFront.triggered.connect(self.onToolBarViewFront)         # type: ignore
        self._toolBarViewBack.triggered.connect(self.onToolBarViewBack)           # type: ignore
        self._toolBarViewTop.triggered.connect(self.onToolBarViewTop)             # type: ignore
        self._toolBarViewBottom.triggered.connect(self.onToolBarViewBottom)       # type: ignore
        self._toolBarViewLeft.triggered.connect(self.onToolBarViewLeft)           # type: ignore
        self._toolBarViewRight.triggered.connect(self.onToolBarViewRight)         # type: ignore
        self._toolBarViewIsometric.triggered.connect(self.onToolBarViewIsometric) # type: ignore

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
        self._viewport.setMeshRenderObject(self._modelDatabase.mesh, render=False)
        # set correct camera view
        if self._modelDatabase.mesh.modelingSpace == ModelingSpaces.TwoDimensional: self._viewport.setView(Views.Front)
        else: self._viewport.setView(Views.Isometric)

#-----------------------------------------------------------------------------------------------------------------------
# Tree -> Viewport
#-----------------------------------------------------------------------------------------------------------------------

    def onModelTreeSelection(self) -> None:
        '''On model tree current item changed.'''
        self._viewport.info.clear()
        self._viewport.setSelectionRenderObject(None, render=False)
        dataObject: DataObject | None = self._modelTree.currentDataObject()
        match dataObject:
            case NodeSet():
                color: tuple[float, float, float] = (1.0, 0.0, 0.0)
                self._viewport.info.setText(1, 'Edit Node Set')
                self._viewport.info.setText(0, 'Use Viewport Pickers to Add/Remove Nodes')
            case ElementSet():
                color: tuple[float, float, float] = (1.0, 0.0, 0.0)
                self._viewport.info.setText(1, 'Edit Element Set')
                self._viewport.info.setText(0, 'Use Viewport Pickers to Add/Remove Elements')
            case _:
                self._viewport.render()
                return
        self._viewport.setSelectionRenderObject(dataObject, color)

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

#-----------------------------------------------------------------------------------------------------------------------
# Tool Bar
#-----------------------------------------------------------------------------------------------------------------------

    def onToolBarFileNew(self) -> None:
        '''On Tool Bar > File > New.'''
        self.onMenuBarFileNew()

    def onToolBarViewFront(self) -> None:
        '''On Tool Bar > View > Front.'''
        self._viewport.setView(Views.Front)

    def onToolBarViewBack(self) -> None:
        '''On Tool Bar > View > Back.'''
        self._viewport.setView(Views.Back)

    def onToolBarViewTop(self) -> None:
        '''On Tool Bar > View > Top.'''
        self._viewport.setView(Views.Top)

    def onToolBarViewBottom(self) -> None:
        '''On Tool Bar > View > Bottom.'''
        self._viewport.setView(Views.Bottom)

    def onToolBarViewLeft(self) -> None:
        '''On Tool Bar > View > Left.'''
        self._viewport.setView(Views.Left)

    def onToolBarViewRight(self) -> None:
        '''On Tool Bar > View > Right.'''
        self._viewport.setView(Views.Right)

    def onToolBarViewIsometric(self) -> None:
        '''On Tool Bar > View > Isometric.'''
        self._viewport.setView(Views.Isometric)
