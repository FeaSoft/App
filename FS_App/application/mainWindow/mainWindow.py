from os import path
from typing import Literal, Any, cast
from collections.abc import Callable, Sequence
from dataModel import (
    ModelingSpaces, DataObject, NodeSet, ElementSet, Section, ConcentratedLoad, BoundaryCondition, ModelDatabase
)
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
        Viewport.registerCallback(self.onViewportOptionChanged)
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
        pickSingle: bool,
        pickMultiple: bool,
        pickTarget: Literal['Points', 'Cells'] | None,
        onPicked: Callable[[Sequence[int], bool], None] | None
    ) -> None:
        '''Enables picking.'''
        self._viewport.setPickAction(onPicked, pickTarget)
        if pickSingle: self._toolBarInteractionPickSingle.setEnabled(True)
        if pickMultiple: self._toolBarInteractionPickMultiple.setEnabled(True)

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
        # clear viewport info and current selection
        self._viewport.info.clear()
        self._viewport.setSelectionRenderObject(None, render=False)

        # if no data object is selected or no model database is loaded:
        # disable picking, render scene, and return
        dataObject: DataObject | None = self._modelTree.currentDataObject()
        if not dataObject or not self._modelDatabase:
            self.disablePicking()
            self._viewport.render()
            return

        # render viewport selection based on currently selected data object
        stopPicking: bool = True
        match dataObject:
            case NodeSet():
                stopPicking = False
                self.enablePicking(True, True, 'Points', lambda x, y: self.onViewportPick(dataObject, x, y))
                self._viewport.info.setText(1, 'Edit Node Set')
                self._viewport.info.setText(0, 'Use Viewport Pickers to Add/Remove Nodes')
                self._viewport.setSelectionRenderObject(dataObject, (1.0, 0.0, 0.0), render=False)
            case ElementSet():
                stopPicking = False
                self.enablePicking(True, True, 'Cells', lambda x, y: self.onViewportPick(dataObject, x, y))
                self._viewport.info.setText(1, 'Edit Element Set')
                self._viewport.info.setText(0, 'Use Viewport Pickers to Add/Remove Elements')
                self._viewport.setSelectionRenderObject(dataObject, (1.0, 0.0, 0.0), render=False)
            case Section():
                if dataObject.elementSetName != '<Undefined>':
                    dataObject = cast(ElementSet, self._modelDatabase.elementSets[dataObject.elementSetName])
                    self._viewport.setSelectionRenderObject(dataObject, (0.0, 0.75, 0.0), render=False)
            case ConcentratedLoad():
                if dataObject.nodeSetName != '<Undefined>':
                    self._viewport.setSelectionRenderObject(
                        dataObject, (1.0, 1.0, 0.0), self._modelDatabase, render=False
                    )
            case BoundaryCondition():
                if dataObject.nodeSetName != '<Undefined>':
                    self._viewport.setSelectionRenderObject(
                        dataObject, (1.0, 0.5, 0.0), self._modelDatabase, render=False
                    )
            case _:
                pass
        if stopPicking: self.disablePicking()
        self._viewport.render()

    def onViewportPick(self, dataObject: NodeSet | ElementSet, indices: Sequence[int], remove: bool) -> None:
        '''On viewport picking action performed.'''
        if remove: dataObject.remove(indices)
        else: dataObject.add(indices)

#-----------------------------------------------------------------------------------------------------------------------
# Viewport -> Main Window
#-----------------------------------------------------------------------------------------------------------------------

    def onViewportOptionChanged(self, optionName: str, optionValue: Any) -> None:
        '''On viewport global option changed.'''
        match optionName:
            case InteractionStyles.__name__:
                # uncheck all buttons in the interaction tool bar
                for action in (
                    self._toolBarInteractionRotate, self._toolBarInteractionPan, self._toolBarInteractionZoom,
                    self._toolBarInteractionPickSingle, self._toolBarInteractionPickMultiple,
                    self._toolBarInteractionProbe, self._toolBarInteractionRuler
                ): action.setChecked(False)
                # check corresponding button
                match cast(InteractionStyles, optionValue):
                    case InteractionStyles.Rotate:       self._toolBarInteractionRotate.setChecked(True)
                    case InteractionStyles.Pan:          self._toolBarInteractionPan.setChecked(True)
                    case InteractionStyles.Zoom:         self._toolBarInteractionZoom.setChecked(True)
                    case InteractionStyles.PickSingle:   self._toolBarInteractionPickSingle.setChecked(True)
                    case InteractionStyles.PickMultiple: self._toolBarInteractionPickMultiple.setChecked(True)
                    case InteractionStyles.Probe:        self._toolBarInteractionProbe.setChecked(True)
                    case InteractionStyles.Ruler:        self._toolBarInteractionRuler.setChecked(True)
                # enable picking if necessary
                match cast(InteractionStyles, optionValue):
                    case InteractionStyles.PickSingle | InteractionStyles.PickMultiple:
                        self.onModelTreeSelection() # will enable picking based on selected data object
                    case _: pass

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

    def onToolBarInteractionRotate(self) -> None:
        '''On Tool Bar > Interaction > Rotate.'''
        Viewport.setInteractionStyle(InteractionStyles.Rotate)

    def onToolBarInteractionPan(self) -> None:
        '''On Tool Bar > Interaction > Pan.'''
        Viewport.setInteractionStyle(InteractionStyles.Pan)

    def onToolBarInteractionZoom(self) -> None:
        '''On Tool Bar > Interaction > Zoom.'''
        Viewport.setInteractionStyle(InteractionStyles.Zoom)

    def onToolBarInteractionPickSingle(self) -> None:
        '''On Tool Bar > Interaction > Pick Single.'''
        Viewport.setInteractionStyle(InteractionStyles.PickSingle)

    def onToolBarInteractionPickMultiple(self) -> None:
        '''On Tool Bar > Interaction > Pick Multiple.'''
        Viewport.setInteractionStyle(InteractionStyles.PickMultiple)

    def onToolBarInteractionProbe(self) -> None:
        '''On Tool Bar > Interaction > Probe.'''
        Viewport.setInteractionStyle(InteractionStyles.Probe)

    def onToolBarInteractionRuler(self) -> None:
        '''On Tool Bar > Interaction > Ruler.'''
        Viewport.setInteractionStyle(InteractionStyles.Ruler)
