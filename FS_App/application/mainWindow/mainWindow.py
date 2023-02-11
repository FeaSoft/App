import os.path
from typing import Literal, Any, cast
from collections.abc import Callable, Sequence
from dataModel import (
    ModelingSpaces, DataObject, NodeSet, ElementSet, Section, ConcentratedLoad, BoundaryCondition, ModelDatabase,
    OutputDatabase
)
from inputOutput import AbaqusReader, FSWriter, FSReader
from visualization import Viewport, Views, InteractionStyles
from application.terminal import Terminal
from application.mainWindow.mainWindowShell import MainWindowShell
from PySide6.QtWidgets import QFileDialog, QMessageBox
from PySide6.QtGui import QCloseEvent

class MainWindow(MainWindowShell):
    '''
    The main window.
    '''

    @property
    def terminal(self) -> Terminal:
        '''The Python terminal.'''
        return self._terminal

    @property
    def currentViewport(self) -> Viewport:
        '''The current visualization viewport.'''
        match self._module:
            case 'Preprocessor': return self._modelViewport
            case 'Visualization': return self._outputViewport

    # attribute slots
    __slots__ = ('_module', '_modelDatabase', '_outputDatabase')

    def __init__(self) -> None:
        '''Main window constructor.'''
        super().__init__()
        # module
        self._module: Literal['Preprocessor', 'Visualization'] = 'Preprocessor'
        # databases
        self._modelDatabase: ModelDatabase | None = None
        self._outputDatabase: OutputDatabase | None = None
        # update window title
        self.updateWindowTitle()
        # setup connections
        Viewport.registerCallback(self.onViewportOptionChanged)
        self._modelTree.currentItemChanged.connect(self.onModelTreeSelection)                         # type: ignore
        self._outputTree.currentItemChanged.connect(self.onOutputTreeSelection)                       # type: ignore
        self._menuBarFileNew.triggered.connect(self.onMenuBarFileNew)                                 # type: ignore
        self._menuBarFileOpen.triggered.connect(self.onMenuBarFileOpen)                               # type: ignore
        self._menuBarFileSave.triggered.connect(self.onMenuBarFileSave)                               # type: ignore
        self._menuBarFileSaveAs.triggered.connect(self.onMenuBarFileSaveAs)                           # type: ignore
        self._menuBarFileClose.triggered.connect(self.onMenuBarFileClose)                             # type: ignore
        self._menuBarFileExit.triggered.connect(self.onMenuBarFileExit)                               # type: ignore
        self._menuBarModulePreprocessor.triggered.connect(self.onMenuBarModulePreprocessor)           # type: ignore
        self._menuBarModuleVisualization.triggered.connect(self.onMenuBarModuleVisualization)         # type: ignore
        self._menuBarSolverDialog.triggered.connect(self.onMenuBarSolverDialog)                       # type: ignore
        self._menuBarOptionsCommon.triggered.connect(self.onMenuBarOptionsCommon)                     # type: ignore
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
        self._toolBarCellSurface.triggered.connect(self.onToolBarCellSurface)                         # type: ignore
        self._toolBarCellWireframe.triggered.connect(self.onToolBarCellWireframe)                     # type: ignore
        self._toolBarProjectionPerspective.triggered.connect(self.onToolBarProjectionPerspective)     # type: ignore
        self._toolBarProjectionParallel.triggered.connect(self.onToolBarProjectionParallel)           # type: ignore
        self._toolBarLightingOn.triggered.connect(self.onToolBarLightingOn)                           # type: ignore
        self._toolBarLightingOff.triggered.connect(self.onToolBarLightingOff)                         # type: ignore
        self._toolBarInteractionRotate.triggered.connect(self.onToolBarInteractionRotate)             # type: ignore
        self._toolBarInteractionPan.triggered.connect(self.onToolBarInteractionPan)                   # type: ignore
        self._toolBarInteractionZoom.triggered.connect(self.onToolBarInteractionZoom)                 # type: ignore
        self._toolBarInteractionPickSingle.triggered.connect(self.onToolBarInteractionPickSingle)     # type: ignore
        self._toolBarInteractionPickMultiple.triggered.connect(self.onToolBarInteractionPickMultiple) # type: ignore
        self._toolBarInteractionProbe.triggered.connect(self.onToolBarInteractionProbe)               # type: ignore
        self._toolBarInteractionRuler.triggered.connect(self.onToolBarInteractionRuler)               # type: ignore

    def updateWindowTitle(self) -> None:
        '''Sets the current window title.'''
        title: str = f'FeaSoft - {self._module} Module'
        if self._module == 'Preprocessor' and self._modelDatabase: title += f' - {self._modelDatabase.filePath}'
        elif self._module == 'Visualization' and self._outputDatabase: title += f' - {self._outputDatabase.filePath}'
        self.setWindowTitle(title)

    def show(self) -> None:
        '''
        Shows the widget and its child widgets.
        Initializes the viewport.
        '''
        super().show()
        self._modelViewport.initialize()
        self._outputViewport.initialize()

    def closeEvent(self, event: QCloseEvent) -> None:
        '''Window close event.'''
        super().closeEvent(event)
        self._modelViewport.finalize()
        self._outputViewport.finalize()

    def enablePicking(
        self,
        pickSingle: bool,
        pickMultiple: bool,
        pickTarget: Literal['Points', 'Cells'] | None,
        onPicked: Callable[[Sequence[int], bool], None] | None
    ) -> None:
        '''Enables picking.'''
        Viewport.setPickAction(onPicked, pickTarget)
        if pickSingle: self._toolBarInteractionPickSingle.setEnabled(True)
        if pickMultiple: self._toolBarInteractionPickMultiple.setEnabled(True)

    def disablePicking(self) -> None:
        '''Disables picking.'''
        Viewport.setPickAction(None, None)
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
            extension: str = os.path.splitext(filePath)[1]
            match extension:
                case '.inp': self._modelDatabase = AbaqusReader.readModelDatabase(filePath)
                case '.fs_mdb': self._modelDatabase = FSReader.readModelDatabase(filePath)
                case _: raise ValueError(f"invalid file extension: '{extension}'")
        # update model tree and model viewport
        self._modelTree.setModelDatabase(self._modelDatabase)
        self._modelViewport.setGridRenderObject(
            self._modelDatabase.mesh if self._modelDatabase else None,
            isDeformable=False,
            render=False
        )
        # set correct camera view
        if self._modelDatabase and self._modelDatabase.mesh.modelingSpace == ModelingSpaces.ThreeDimensional:
            self._modelViewport.setView(Views.Isometric)
        else:
            self._modelViewport.setView(Views.Front)
        # open preprocessor module
        if self._module != 'Preprocessor': self.setModule('Preprocessor')
        # update window title
        self.updateWindowTitle()

    def setOutputDatabase(self, filePath: str | None) -> None:
        '''
        Creates an output database from file.
        Updates the GUI based on the new output database.
        '''
        # if a file is not given, dereference the output database
        if not filePath:
            self._outputDatabase = None
        else:
            # create output database from file
            extension: str = os.path.splitext(filePath)[1]
            match extension:
                case '.fs_odb': self._outputDatabase = FSReader.readOutputDatabase(filePath)
                case _: raise ValueError(f"invalid file extension: '{extension}'")
        # update output tree and output viewport
        self._outputTree.setOutputDatabase(self._outputDatabase)
        self._outputViewport.setGridRenderObject(
            self._outputDatabase.mesh if self._outputDatabase else None,
            isDeformable=True,
            render=False
        )
        # set correct camera view
        if self._outputDatabase and self._outputDatabase.mesh.modelingSpace == ModelingSpaces.ThreeDimensional:
            self._outputViewport.setView(Views.Isometric)
        else:
            self._outputViewport.setView(Views.Front)
        # open visualization module
        if self._module != 'Visualization': self.setModule('Visualization')
        # update window title
        self.updateWindowTitle()

    def setModule(self, module: Literal['Preprocessor', 'Visualization']) -> None:
        '''Updates the view based on the given module.'''
        # update global flag
        self._module = module
        # convenient flags
        isPreprocessor: bool = self._module == 'Preprocessor'
        isVisualization: bool = self._module == 'Visualization'
        # change viewport (avoid showing two viewports at the same time or they will flicker)
        if isPreprocessor:
            self._outputViewport.setVisible(False)
            self._modelViewport.setVisible(True)
        elif isVisualization:
            self._modelViewport.setVisible(False)
            self._outputViewport.setVisible(True)
        # preprocessor module
        self._menuBarModulePreprocessor.setChecked(isPreprocessor)
        self._menuBarSolver.menuAction().setVisible(isPreprocessor)
        if self._solverDialog.isVisible() and not isPreprocessor: self._solverDialog.close()
        self._modelTree.setVisible(isPreprocessor)
        # visualization module
        self._menuBarModuleVisualization.setChecked(isVisualization)
        self._outputTree.setVisible(isVisualization)
        # update window title
        self.updateWindowTitle()

#-----------------------------------------------------------------------------------------------------------------------
# Tree -> Viewport
#-----------------------------------------------------------------------------------------------------------------------

    def onModelTreeSelection(self) -> None:
        '''On model tree current item changed.'''
        # clear viewport info and current selection
        self._modelViewport.info.clear()
        self._modelViewport.setSelectionRenderObject(None, render=False)

        # if no data object is selected or no model database is loaded:
        # disable picking, render scene, and return
        dataObject: DataObject | None = self._modelTree.currentDataObject()
        if not dataObject or not self._modelDatabase:
            self.disablePicking()
            self._modelViewport.render()
            return

        # render viewport selection based on currently selected data object
        stopPicking: bool = True
        match dataObject:
            case NodeSet():
                stopPicking = False
                self.enablePicking(True, True, 'Points', lambda x, y: self.onViewportPick(dataObject, x, y))
                self._modelViewport.info.setText(1, 'Edit Node Set')
                self._modelViewport.info.setText(0, 'Use Viewport Pickers to Add/Remove Nodes')
                self._modelViewport.setSelectionRenderObject(dataObject, (1.0, 0.0, 0.0), render=False)
            case ElementSet():
                stopPicking = False
                self.enablePicking(True, True, 'Cells', lambda x, y: self.onViewportPick(dataObject, x, y))
                self._modelViewport.info.setText(1, 'Edit Element Set')
                self._modelViewport.info.setText(0, 'Use Viewport Pickers to Add/Remove Elements')
                self._modelViewport.setSelectionRenderObject(dataObject, (1.0, 0.0, 0.0), render=False)
            case Section():
                if dataObject.elementSetName != '<Undefined>':
                    dataObject = cast(ElementSet, self._modelDatabase.elementSets[dataObject.elementSetName])
                    self._modelViewport.setSelectionRenderObject(dataObject, (0.0, 0.75, 0.0), render=False)
            case ConcentratedLoad():
                if dataObject.nodeSetName != '<Undefined>':
                    self._modelViewport.setSelectionRenderObject(
                        dataObject, (1.0, 1.0, 0.0), self._modelDatabase, render=False
                    )
            case BoundaryCondition():
                if dataObject.nodeSetName != '<Undefined>':
                    self._modelViewport.setSelectionRenderObject(
                        dataObject, (1.0, 0.5, 0.0), self._modelDatabase, render=False
                    )
            case _:
                pass
        if stopPicking: self.disablePicking()
        self._modelViewport.render()

    def onOutputTreeSelection(self) -> None:
        '''On output tree current item changed.'''
        # clear viewport info, previous plot, and reset deformation
        self._outputViewport.info.clear()
        self._outputViewport.plotNodalScalarField(None, render=False)
        self._outputViewport.setGridDeformation(None, render=False)

        # if nothing is selected or no output database is loaded:
        # render scene and return
        selection = self._outputTree.currentSelection()
        if not selection or not self._outputDatabase:
            self._outputViewport.render()
            return

        # match selection type
        match selection[0]:
            case 'History':
                frame, historyName = cast(tuple[int, str], selection[1])
                print(f'{historyName} at frame {frame + 1}: {self._outputDatabase.history(frame, historyName)}')
            case 'Field':
                frame, groupName, fieldName = cast(tuple[int, str, str], selection[1])
                self._outputViewport.info.setText(2, fieldName)
                self._outputViewport.info.setText(1, self._outputDatabase.frameDescription(frame))
                self._outputViewport.info.setText(0, 'Deformation Scale Factor: 0.0')
                self._outputViewport.plotNodalScalarField(
                    self._outputDatabase.nodalScalarField(frame, groupName, fieldName),
                    render=False
                )
                self._outputViewport.setGridDeformation(self._outputDatabase.nodalDisplacements(frame), render=False)
        self._outputViewport.render()

#-----------------------------------------------------------------------------------------------------------------------
# Viewport -> Tree
#-----------------------------------------------------------------------------------------------------------------------

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
            case 'InteractionStyle':
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
            case 'GridCellRepresentation':
                self._toolBarCellSurface.setChecked(optionValue == 'Surface')
                self._toolBarCellWireframe.setChecked(optionValue == 'Wireframe')
            case 'Projection':
                self._toolBarProjectionPerspective.setChecked(optionValue == 'Perspective')
                self._toolBarProjectionParallel.setChecked(optionValue == 'Parallel')
            case 'Lighting':
                self._toolBarLightingOn.setChecked(optionValue == 'On')
                self._toolBarLightingOff.setChecked(optionValue == 'Off')
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
            if os.path.isfile(os.path.splitext(filePath)[0] + '.fs_mdb'):
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
            filter='FeaSoft Model Database Files (*.fs_mdb);;FeaSoft Output Database Files (*.fs_odb);;All Files (*.*)',
            options=QFileDialog.Option.DontUseNativeDialog
        )[0]
        if filePath != '':
            extension: str = os.path.splitext(filePath)[1]
            match extension:
                case '.fs_mdb':
                    self.setModelDatabase(filePath)
                    if self._modelDatabase:
                        print(f"Model database opened: '{self._modelDatabase.filePath}'")
                case '.fs_odb':
                    self.setOutputDatabase(filePath)
                    if self._outputDatabase:
                        print(f"Output database opened: '{self._outputDatabase.filePath}'")
                case _:
                    raise ValueError(f"invalid file extension: '{extension}'")

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
            self._modelDatabase.filePath = os.path.splitext(filePath)[0] + '.fs_mdb'
            FSWriter.writeModelDatabase(self._modelDatabase)
            print(f"Model database saved: '{self._modelDatabase.filePath}'")
            # update window title
            self.updateWindowTitle()

    def onMenuBarFileClose(self) -> None:
        '''On Menu Bar > File > Close.'''
        match self._module:
            case 'Preprocessor':
                if not self._modelDatabase:
                    raise RuntimeError('a model database must first be opened')
                self.setModelDatabase(None)
                print('Model database closed')
            case 'Visualization':
                if not self._outputDatabase:
                    raise RuntimeError('an output database must first be opened')
                self.setOutputDatabase(None)
                print('Output database closed')

    def onMenuBarFileExit(self) -> None:
        '''On Menu Bar > File > Exit.'''
        self.close()

    def onMenuBarModulePreprocessor(self) -> None:
        '''On Menu Bar > Module > Preprocessor.'''
        self.setModule('Preprocessor')

    def onMenuBarModuleVisualization(self) -> None:
        '''On Menu Bar > Module > Visualization.'''
        self.setModule('Visualization')

    def onMenuBarSolverDialog(self) -> None:
        '''On Menu Bar > Solver > Dialog.'''
        self._solverDialog.show()

    def onMenuBarOptionsCommon(self) -> None:
        '''On Menu Bar > Options > Common.'''
        self._optionsCommonDialog.show()

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
        self.currentViewport.setView(Views.Front)

    def onToolBarViewBack(self) -> None:
        '''On Tool Bar > View > Back.'''
        self.currentViewport.setView(Views.Back)

    def onToolBarViewTop(self) -> None:
        '''On Tool Bar > View > Top.'''
        self.currentViewport.setView(Views.Top)

    def onToolBarViewBottom(self) -> None:
        '''On Tool Bar > View > Bottom.'''
        self.currentViewport.setView(Views.Bottom)

    def onToolBarViewLeft(self) -> None:
        '''On Tool Bar > View > Left.'''
        self.currentViewport.setView(Views.Left)

    def onToolBarViewRight(self) -> None:
        '''On Tool Bar > View > Right.'''
        self.currentViewport.setView(Views.Right)

    def onToolBarViewIsometric(self) -> None:
        '''On Tool Bar > View > Isometric.'''
        self.currentViewport.setView(Views.Isometric)

    def onToolBarCellSurface(self) -> None:
        '''On Tool Bat > Cell > Surface.'''
        Viewport.setGridCellRepresentation('Surface')

    def onToolBarCellWireframe(self) -> None:
        '''On Tool Bat > Cell > Wireframe.'''
        Viewport.setGridCellRepresentation('Wireframe')

    def onToolBarProjectionPerspective(self) -> None:
        '''On Tool Bat > Projection > Perspective.'''
        Viewport.setProjection('Perspective')

    def onToolBarProjectionParallel(self) -> None:
        '''On Tool Bat > Projection > Parallel.'''
        Viewport.setProjection('Parallel')

    def onToolBarLightingOn(self) -> None:
        '''On Tool Bat > Lighting > On.'''
        Viewport.setLighting('On')

    def onToolBarLightingOff(self) -> None:
        '''On Tool Bat > Lighting > Off.'''
        Viewport.setLighting('Off')

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
