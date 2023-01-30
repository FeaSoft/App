from os import path
from typing import Literal
from collections.abc import Callable, Sequence
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
        self._modelTree.currentItemChanged.connect(self.onModelTreeSelection)                         # type: ignore
        self._menuBarFileNew.triggered.connect(self.onMenuBarFileNew)                                 # type: ignore
        self._toolBarFileNew.triggered.connect(self.onToolBarFileNew)                                 # type: ignore
        self._toolBarViewFront.triggered.connect(self.onToolBarViewFront)                             # type: ignore
        self._toolBarViewBack.triggered.connect(self.onToolBarViewBack)                               # type: ignore
        self._toolBarViewTop.triggered.connect(self.onToolBarViewTop)                                 # type: ignore
        self._toolBarViewBottom.triggered.connect(self.onToolBarViewBottom)                           # type: ignore
        self._toolBarViewLeft.triggered.connect(self.onToolBarViewLeft)                               # type: ignore
        self._toolBarViewRight.triggered.connect(self.onToolBarViewRight)                             # type: ignore
        self._toolBarViewIsometric.triggered.connect(self.onToolBarViewIsometric)                     # type: ignore
        self._toolBarInteractionRotate.triggered.connect(self.onToolBarInteractionRotate)             # type: ignore
        self._toolBarInteractionPan.triggered.connect(self.onToolBarInteractionPan)                   # type: ignore
        self._toolBarInteractionZoom.triggered.connect(self.onToolBarInteractionZoom)                 # type: ignore
        self._toolBarInteractionPickSingle.triggered.connect(self.onToolBarInteractionPickSingle)     # type: ignore
        self._toolBarInteractionPickMultiple.triggered.connect(self.onToolBarInteractionPickMultiple) # type: ignore
        self._toolBarInteractionProbe.triggered.connect(self.onToolBarInteractionProbe)               # type: ignore
        self._toolBarInteractionRuler.triggered.connect(self.onToolBarInteractionRuler)               # type: ignore

    def show(self) -> None:
        '''
        Shows the widget and its child widgets.
        Initializes the viewport.
        '''
        super().show()
        self._viewport.initialize()

    def enablePicking(
        self,
        single: bool,
        multiple: bool,
        pickTarget: Literal['Points', 'Cells'] | None,
        onPicked: Callable[[Sequence[int], bool], None] | None
    ) -> None:
        '''Enables picking.'''
        self._viewport.setPickAction(onPicked, pickTarget)
        if single: self._toolBarInteractionPickSingle.setEnabled(True)
        if multiple: self._toolBarInteractionPickMultiple.setEnabled(True)

    def disablePicking(self) -> None:
        '''Disables picking.'''
        self._viewport.setPickAction(None, None)
        if self._toolBarInteractionPickSingle.isChecked() or self._toolBarInteractionPickMultiple.isChecked():
            self._toolBarInteractionRotate.trigger()
        self._toolBarInteractionPickSingle.setEnabled(False)
        self._toolBarInteractionPickMultiple.setEnabled(False)

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
                self.enablePicking(True, True, 'Points', lambda x, y: self.onViewportPick(dataObject, x, y))
                color: tuple[float, float, float] = (1.0, 0.0, 0.0)
                self._viewport.info.setText(1, 'Edit Node Set')
                self._viewport.info.setText(0, 'Use Viewport Pickers to Add/Remove Nodes')
            case ElementSet():
                self.enablePicking(True, True, 'Cells', lambda x, y: self.onViewportPick(dataObject, x, y))
                color: tuple[float, float, float] = (1.0, 0.0, 0.0)
                self._viewport.info.setText(1, 'Edit Element Set')
                self._viewport.info.setText(0, 'Use Viewport Pickers to Add/Remove Elements')
            case _:
                self.disablePicking()
                self._viewport.render()
                return
        self._viewport.setSelectionRenderObject(dataObject, color)

    def onViewportPick(self, dataObject: NodeSet | ElementSet, indices: Sequence[int], remove: bool) -> None:
        '''On viewport picking action performed.'''
        if remove: dataObject.remove(indices)
        else: dataObject.add(indices)
        self._viewport.setSelectionRenderObject(dataObject, (1.0, 0.0, 0.0))

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

    def uncheckToolBarInteraction(self) -> None:
        '''Unchecks all buttons in the interaction tool bar.'''
        self._toolBarInteractionRotate.setChecked(False)
        self._toolBarInteractionPan.setChecked(False)
        self._toolBarInteractionZoom.setChecked(False)
        self._toolBarInteractionPickSingle.setChecked(False)
        self._toolBarInteractionPickMultiple.setChecked(False)
        self._toolBarInteractionProbe.setChecked(False)
        self._toolBarInteractionRuler.setChecked(False)

    def onToolBarInteractionRotate(self) -> None:
        '''On Tool Bar > Interaction > Rotate.'''
        if not self._toolBarInteractionRotate.isChecked():
            self._toolBarInteractionRotate.setChecked(True)
            return
        self.uncheckToolBarInteraction()
        self._toolBarInteractionRotate.setChecked(True)
        self._viewport.setInteractionStyle(InteractionStyles.Rotate)

    def onToolBarInteractionPan(self) -> None:
        '''On Tool Bar > Interaction > Pan.'''
        if not self._toolBarInteractionPan.isChecked():
            self._toolBarInteractionPan.setChecked(True)
            return
        self.uncheckToolBarInteraction()
        self._toolBarInteractionPan.setChecked(True)
        self._viewport.setInteractionStyle(InteractionStyles.Pan)

    def onToolBarInteractionZoom(self) -> None:
        '''On Tool Bar > Interaction > Zoom.'''
        if not self._toolBarInteractionZoom.isChecked():
            self._toolBarInteractionZoom.setChecked(True)
            return
        self.uncheckToolBarInteraction()
        self._toolBarInteractionZoom.setChecked(True)
        self._viewport.setInteractionStyle(InteractionStyles.Zoom)

    def onToolBarInteractionPickSingle(self) -> None:
        '''On Tool Bar > Interaction > Pick Single.'''
        if not self._toolBarInteractionPickSingle.isChecked():
            self._toolBarInteractionPickSingle.setChecked(True)
            return
        self.uncheckToolBarInteraction()
        self._toolBarInteractionPickSingle.setChecked(True)
        self._viewport.setInteractionStyle(InteractionStyles.PickSingle)
        self.onModelTreeSelection() # in order to enable picking

    def onToolBarInteractionPickMultiple(self) -> None:
        '''On Tool Bar > Interaction > Pick Multiple.'''
        if not self._toolBarInteractionPickMultiple.isChecked():
            self._toolBarInteractionPickMultiple.setChecked(True)
            return
        self.uncheckToolBarInteraction()
        self._toolBarInteractionPickMultiple.setChecked(True)
        self._viewport.setInteractionStyle(InteractionStyles.PickMultiple)
        self.onModelTreeSelection() # in order to enable picking

    def onToolBarInteractionProbe(self) -> None:
        '''On Tool Bar > Interaction > Probe.'''
        if not self._toolBarInteractionProbe.isChecked():
            self._toolBarInteractionProbe.setChecked(True)
            return
        self.uncheckToolBarInteraction()
        self._toolBarInteractionProbe.setChecked(True)
        print('probe')

    def onToolBarInteractionRuler(self) -> None:
        '''On Tool Bar > Interaction > Ruler.'''
        if not self._toolBarInteractionRuler.isChecked():
            self._toolBarInteractionRuler.setChecked(True)
            return
        self.uncheckToolBarInteraction()
        self._toolBarInteractionRuler.setChecked(True)
        print('ruler')
