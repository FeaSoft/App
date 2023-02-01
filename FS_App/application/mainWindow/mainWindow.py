from os import path
from typing import Literal, Any, cast
from collections.abc import Callable, Sequence
from dataModel import (
    ModelingSpaces, DataObject, NodeSet, ElementSet, Section, ConcentratedLoad, BoundaryCondition, ModelDatabase
)
from inputOutput import AbaqusReader, FSWriter, FSReader
from visualization import Viewport, Views, InteractionStyles
from application.terminal import Terminal
from application.mainWindow.mainWindowShell import MainWindowShell
from PySide6.QtWidgets import QFileDialog, QMessageBox

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
        self._menuBarFileOpen.triggered.connect(self.onMenuBarFileOpen)                               # type: ignore
        self._menuBarFileSave.triggered.connect(self.onMenuBarFileSave)                               # type: ignore
        self._menuBarFileSaveAs.triggered.connect(self.onMenuBarFileSaveAs)                           # type: ignore
        self._menuBarFileClose.triggered.connect(self.onMenuBarFileClose)                             # type: ignore
        self._menuBarFileExit.triggered.connect(self.onMenuBarFileExit)                               # type: ignore
        self._toolBarFileNew.triggered.connect(self.onToolBarFileNew)                                 # type: ignore
        self._toolBarFileOpen.triggered.connect(self.onToolBarFileOpen)                               # type: ignore
        self._toolBarFileSave.triggered.connect(self.onToolBarFileSave)                               # type: ignore
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

    def setModelDatabase(self, filePath: str | None) -> None:
        '''
        Creates a model database from file.
        Updates the GUI based on the new model database.
        '''
        # if a file is not given, dereference the model database
        if not filePath:
            self._modelDatabase = None
        else:
            # create model database from file
            extension: str = path.splitext(filePath)[1]
            match extension:
                case '.inp': self._modelDatabase = AbaqusReader.readModelDatabase(filePath)
                case '.fs_mdb': self._modelDatabase = FSReader.readModelDatabase(filePath)
                case _: raise ValueError(f"invalid file extension: '{extension}'")
        # update model tree and viewport
        self._modelTree.setModelDatabase(self._modelDatabase)
        self._viewport.setMeshRenderObject(self._modelDatabase.mesh if self._modelDatabase else None, render=False)
        # set correct camera view
        if self._modelDatabase and self._modelDatabase.mesh.modelingSpace == ModelingSpaces.ThreeDimensional:
            self._viewport.setView(Views.Isometric)
        else:
            self._viewport.setView(Views.Front)

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
        if filePath != '':
            if path.isfile(path.splitext(filePath)[0] + '.fs_mdb'):
                result: int = QMessageBox.warning(
                    self,
                    'Save Model Database',
                    'A model database already exists.\nDo you want to replace it?',
                    QMessageBox.StandardButton.Yes,
                    QMessageBox.StandardButton.No
                )
                if result != QMessageBox.StandardButton.Yes: return
            self.setModelDatabase(filePath)
            if self._modelDatabase:
                FSWriter.writeModelDatabase(self._modelDatabase)
                print(f"Model database created: '{self._modelDatabase.filePath}'")

    def onMenuBarFileOpen(self) -> None:
        '''On Menu Bar > File > Open.'''
        filePath: str = QFileDialog.getOpenFileName( # type: ignore
            parent=self,
            caption='Open Database',
            filter='FeaSoft Model Database Files (*.fs_mdb);;All Files (*.*)',
            options=QFileDialog.Option.DontUseNativeDialog
        )[0]
        if filePath != '':
            self.setModelDatabase(filePath)
            if self._modelDatabase:
                print(f"Model database opened: '{self._modelDatabase.filePath}'")

    def onMenuBarFileSave(self) -> None:
        '''On Menu Bar > File > Save.'''
        if not self._modelDatabase:
            raise RuntimeError('a model database must first be opened')
        FSWriter.writeModelDatabase(self._modelDatabase)
        print(f"Model database saved: '{self._modelDatabase.filePath}'")

    def onMenuBarFileSaveAs(self) -> None:
        '''On Menu Bar > File > Save As.'''
        if not self._modelDatabase:
            raise RuntimeError('a model database must first be opened')
        filePath: str = QFileDialog.getSaveFileName( # type: ignore
            parent=self,
            caption='Save Model Database',
            filter='FeaSoft Model Database Files (*.fs_mdb)',
            options=QFileDialog.Option.DontUseNativeDialog
        )[0]
        if filePath != '':
            self._modelDatabase.filePath = path.splitext(filePath)[0] + '.fs_mdb'
            FSWriter.writeModelDatabase(self._modelDatabase)
            print(f"Model database saved: '{self._modelDatabase.filePath}'")

    def onMenuBarFileClose(self) -> None:
        '''On Menu Bar > File > Close.'''
        if not self._modelDatabase:
            raise RuntimeError('a model database must first be opened')
        self.setModelDatabase(None)
        print('Model database closed')

    def onMenuBarFileExit(self) -> None:
        '''On Menu Bar > File > Exit.'''
        self.close()

#-----------------------------------------------------------------------------------------------------------------------
# Tool Bar
#-----------------------------------------------------------------------------------------------------------------------

    def onToolBarFileNew(self) -> None:
        '''On Tool Bar > File > New.'''
        self.onMenuBarFileNew()

    def onToolBarFileOpen(self) -> None:
        '''On Tool Bar > File > Open.'''
        self.onMenuBarFileOpen()

    def onToolBarFileSave(self) -> None:
        '''On Tool Bar > File > Save.'''
        self.onMenuBarFileSave()

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
