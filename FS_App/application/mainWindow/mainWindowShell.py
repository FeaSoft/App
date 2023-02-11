from application.terminal import Terminal
from application.solverDialog import SolverDialog
from application.optionsCommonDialog import OptionsCommonDialog
from control import ModelDatabaseControl, OutputDatabaseControl
from visualization import Viewport
from PySide6.QtGui import Qt, QAction, QIcon
from PySide6.QtWidgets import (
    QWidget, QMainWindow, QMenuBar, QMenu, QToolBar, QVBoxLayout, QSplitter, QSizePolicy, QFrame
)

class MainWindowShell(QMainWindow):
    '''
    The main window shell (basic UI).
    '''

#   # attribute slots
#   __slots__ = (
#       '_icons', '_menuBar', '_menuBarFile', '_menuBarFileNew', '_menuBarFileOpen', '_menuBarFileSave',
#       '_menuBarFileSaveAs', '_menuBarFileClose', '_menuBarFileExit', '_menuBarModule', '_menuBarModulePreprocessor',
#       '_menuBarModuleVisualization', '_menuBarSolver', '_menuBarSolverDialog', '_menuBarOptions',
#       '_menuBarOptionsCommon', '_toolBarFile', '_toolBarFileNew', '_toolBarFileOpen', '_toolBarFileSave',
#       '_toolBarView', '_toolBarViewFront', '_toolBarViewBack', '_toolBarViewTop', '_toolBarViewBottom',
#       '_toolBarViewLeft', '_toolBarViewRight', '_toolBarViewIsometric', '_toolBarCell', '_toolBarCellSurface',
#       '_toolBarCellWireframe', '_toolBarProjection', '_toolBarProjectionPerspective', , '_toolBarProjectionParallel',
#       '_toolBarLighting', '_toolBarLightingOn', '_toolBarLightingOff', '_toolBarInteraction',
#       '_toolBarInteractionRotate', '_toolBarInteractionPan', '_toolBarInteractionZoom',
#       '_toolBarInteractionPickSingle', '_toolBarInteractionPickMultiple', '_toolBarInteractionProbe',
#       '_toolBarInteractionRuler', '_centralWidget', '_centralWidgetLayout', '_verticalSplitter',
#       '_horizontalSplitter', '_splitterLeft', '_splitterLeftLayout', '_modelTree', '_outputTree', '_terminal',
#       '_rightSplitter', '_rightSplitterLayout', '_modelViewport', '_outputViewport', '_solverDialog',
#       '_optionsCommonDialog'
#   )

    def __init__(self) -> None:
        '''Main window shell constructor.'''
        super().__init__()

        # load icons
        self._icons: dict[str, QIcon] = {
            x: QIcon(f'./resources/images/{x}.svg') for x in (
                'file-new', 'file-open', 'file-save', 'file-save-as', 'file-close', 'file-exit', 'solver-dialog',
                'options', 'view-front', 'view-back', 'view-top', 'view-bottom', 'view-left', 'view-right',
                'view-isometric', 'cell-surface', 'cell-wireframe', 'projection-perspective', 'projection-parallel',
                'lighting-on', 'lighting-off', 'interaction-style-rotate', 'interaction-style-pan',
                'interaction-style-zoom', 'interaction-style-pick-single', 'interaction-style-pick-multiple',
                'interaction-style-probe', 'interaction-style-ruler'
            )
        }

        # main window (self)
        self.setWindowTitle('FeaSoft')
        self.resize(1080, 720)

        # menu bar
        self._menuBar: QMenuBar = QMenuBar(self)
        self.setMenuBar(self._menuBar)

        # menu bar > file
        self._menuBarFile: QMenu = QMenu(self._menuBar)
        self._menuBarFile.setTitle('File')
        self._menuBar.addAction(self._menuBarFile.menuAction())

        # menu bar > file > new
        self._menuBarFileNew: QAction = QAction(self._menuBarFile)
        self._menuBarFileNew.setText('New...')
        self._menuBarFileNew.setIcon(self._icons['file-new'])
        self._menuBarFile.addAction(self._menuBarFileNew) # type: ignore

        # menu bar > file > open
        self._menuBarFileOpen: QAction = QAction(self._menuBarFile)
        self._menuBarFileOpen.setText('Open...')
        self._menuBarFileOpen.setIcon(self._icons['file-open'])
        self._menuBarFile.addAction(self._menuBarFileOpen) # type: ignore

        # separator
        self._menuBarFile.addSeparator()

        # menu bar > file > save
        self._menuBarFileSave: QAction = QAction(self._menuBarFile)
        self._menuBarFileSave.setText('Save')
        self._menuBarFileSave.setIcon(self._icons['file-save'])
        self._menuBarFile.addAction(self._menuBarFileSave) # type: ignore

        # menu bar > file > save as
        self._menuBarFileSaveAs: QAction = QAction(self._menuBarFile)
        self._menuBarFileSaveAs.setText('Save As...')
        self._menuBarFileSaveAs.setIcon(self._icons['file-save-as'])
        self._menuBarFile.addAction(self._menuBarFileSaveAs) # type: ignore

        # separator
        self._menuBarFile.addSeparator()

        # menu bar > file > close
        self._menuBarFileClose: QAction = QAction(self._menuBarFile)
        self._menuBarFileClose.setText('Close')
        self._menuBarFileClose.setIcon(self._icons['file-close'])
        self._menuBarFile.addAction(self._menuBarFileClose) # type: ignore

        # separator
        self._menuBarFile.addSeparator()

        # menu bar > file > exit
        self._menuBarFileExit: QAction = QAction(self._menuBarFile)
        self._menuBarFileExit.setText('Exit')
        self._menuBarFileExit.setIcon(self._icons['file-exit'])
        self._menuBarFile.addAction(self._menuBarFileExit) # type: ignore

        # menu bar > module
        self._menuBarModule: QMenu = QMenu(self._menuBar)
        self._menuBarModule.setTitle('Module')
        self._menuBar.addAction(self._menuBarModule.menuAction())

        # menu bar > module > preprocessor
        self._menuBarModulePreprocessor: QAction = QAction(self._menuBarModule)
        self._menuBarModulePreprocessor.setCheckable(True)
        self._menuBarModulePreprocessor.setChecked(True)
        self._menuBarModulePreprocessor.setText('Preprocessor')
        self._menuBarModule.addAction(self._menuBarModulePreprocessor) # type: ignore

        # menu bar > module > visualization
        self._menuBarModuleVisualization: QAction = QAction(self._menuBarModule)
        self._menuBarModuleVisualization.setCheckable(True)
        self._menuBarModuleVisualization.setText('Visualization')
        self._menuBarModule.addAction(self._menuBarModuleVisualization) # type: ignore

        # menu bar > solver
        self._menuBarSolver: QMenu = QMenu(self._menuBar)
        self._menuBarSolver.setTitle('Solver')
        self._menuBar.addAction(self._menuBarSolver.menuAction())

        # menu bar > solver > dialog
        self._menuBarSolverDialog: QAction = QAction(self._menuBarSolver)
        self._menuBarSolverDialog.setText('Submit Job')
        self._menuBarSolverDialog.setIcon(self._icons['solver-dialog'])
        self._menuBarSolver.addAction(self._menuBarSolverDialog) # type: ignore

        # menu bar > options
        self._menuBarOptions: QMenu = QMenu(self._menuBar)
        self._menuBarOptions.setTitle('Options')
        self._menuBar.addAction(self._menuBarOptions.menuAction())

        # menu bar > options > common
        self._menuBarOptionsCommon: QAction = QAction(self._menuBarOptions)
        self._menuBarOptionsCommon.setText('Common')
        self._menuBarOptionsCommon.setIcon(self._icons['options'])
        self._menuBarOptions.addAction(self._menuBarOptionsCommon) # type: ignore

        # tool bar (file)
        self._toolBarFile: QToolBar = QToolBar(self)
        self._toolBarFile.setFloatable(False)
        self.addToolBar(self._toolBarFile)

        # tool bar (file) > new
        self._toolBarFileNew: QAction = QAction(self._toolBarFile)
        self._toolBarFileNew.setToolTip('New Model Database')
        self._toolBarFileNew.setIcon(self._icons['file-new'])
        self._toolBarFile.addAction(self._toolBarFileNew)

        # tool bar (file) > open
        self._toolBarFileOpen: QAction = QAction(self._toolBarFile)
        self._toolBarFileOpen.setToolTip('Open Database')
        self._toolBarFileOpen.setIcon(self._icons['file-open'])
        self._toolBarFile.addAction(self._toolBarFileOpen)

        # tool bar (file) > save
        self._toolBarFileSave: QAction = QAction(self._toolBarFile)
        self._toolBarFileSave.setToolTip('Save Model Database')
        self._toolBarFileSave.setIcon(self._icons['file-save'])
        self._toolBarFile.addAction(self._toolBarFileSave)

        # tool bar (view)
        self._toolBarView: QToolBar = QToolBar(self)
        self._toolBarView.setFloatable(False)
        self.addToolBar(self._toolBarView)

        # tool bar (view) > front
        self._toolBarViewFront: QAction = QAction(self._toolBarView)
        self._toolBarViewFront.setToolTip('View Front')
        self._toolBarViewFront.setIcon(self._icons['view-front'])
        self._toolBarView.addAction(self._toolBarViewFront)

        # tool bar (view) > back
        self._toolBarViewBack: QAction = QAction(self._toolBarView)
        self._toolBarViewBack.setToolTip('View Back')
        self._toolBarViewBack.setIcon(self._icons['view-back'])
        self._toolBarView.addAction(self._toolBarViewBack)

        # tool bar (view) > top
        self._toolBarViewTop: QAction = QAction(self._toolBarView)
        self._toolBarViewTop.setToolTip('View Top')
        self._toolBarViewTop.setIcon(self._icons['view-top'])
        self._toolBarView.addAction(self._toolBarViewTop)

        # tool bar (view) > bottom
        self._toolBarViewBottom: QAction = QAction(self._toolBarView)
        self._toolBarViewBottom.setToolTip('View Bottom')
        self._toolBarViewBottom.setIcon(self._icons['view-bottom'])
        self._toolBarView.addAction(self._toolBarViewBottom)

        # tool bar (view) > left
        self._toolBarViewLeft: QAction = QAction(self._toolBarView)
        self._toolBarViewLeft.setToolTip('View Left')
        self._toolBarViewLeft.setIcon(self._icons['view-left'])
        self._toolBarView.addAction(self._toolBarViewLeft)

        # tool bar (view) > right
        self._toolBarViewRight: QAction = QAction(self._toolBarView)
        self._toolBarViewRight.setToolTip('View Right')
        self._toolBarViewRight.setIcon(self._icons['view-right'])
        self._toolBarView.addAction(self._toolBarViewRight)

        # tool bar (view) > isometric
        self._toolBarViewIsometric: QAction = QAction(self._toolBarView)
        self._toolBarViewIsometric.setToolTip('View Isometric')
        self._toolBarViewIsometric.setIcon(self._icons['view-isometric'])
        self._toolBarView.addAction(self._toolBarViewIsometric)

        # tool bar (cell)
        self._toolBarCell: QToolBar = QToolBar(self)
        self._toolBarCell.setFloatable(False)
        self.addToolBar(self._toolBarCell)

        # tool bar (cell) > surface
        self._toolBarCellSurface: QAction = QAction(self._toolBarCell)
        self._toolBarCellSurface.setToolTip('Cell Surface Representation')
        self._toolBarCellSurface.setIcon(self._icons['cell-surface'])
        self._toolBarCellSurface.setCheckable(True)
        self._toolBarCellSurface.setChecked(True)
        self._toolBarCell.addAction(self._toolBarCellSurface)

        # tool bar (cell) > wireframe
        self._toolBarCellWireframe: QAction = QAction(self._toolBarCell)
        self._toolBarCellWireframe.setToolTip('Cell Wireframe Representation')
        self._toolBarCellWireframe.setIcon(self._icons['cell-wireframe'])
        self._toolBarCellWireframe.setCheckable(True)
        self._toolBarCell.addAction(self._toolBarCellWireframe)

        # tool bar (projection)
        self._toolBarProjection: QToolBar = QToolBar(self)
        self._toolBarProjection.setFloatable(False)
        self.addToolBar(self._toolBarProjection)

        # tool bar (projection) > perspective
        self._toolBarProjectionPerspective: QAction = QAction(self._toolBarProjection)
        self._toolBarProjectionPerspective.setToolTip('Perspective Projection')
        self._toolBarProjectionPerspective.setIcon(self._icons['projection-perspective'])
        self._toolBarProjectionPerspective.setCheckable(True)
        self._toolBarProjectionPerspective.setChecked(True)
        self._toolBarProjection.addAction(self._toolBarProjectionPerspective)

        # tool bar (projection) > parallel
        self._toolBarProjectionParallel: QAction = QAction(self._toolBarProjection)
        self._toolBarProjectionParallel.setToolTip('Parallel Projection')
        self._toolBarProjectionParallel.setIcon(self._icons['projection-parallel'])
        self._toolBarProjectionParallel.setCheckable(True)
        self._toolBarProjection.addAction(self._toolBarProjectionParallel)

        # tool bar (lighting)
        self._toolBarLighting: QToolBar = QToolBar(self)
        self._toolBarLighting.setFloatable(False)
        self.addToolBar(self._toolBarLighting)

        # tool bar (lighting) > on
        self._toolBarLightingOn: QAction = QAction(self._toolBarLighting)
        self._toolBarLightingOn.setToolTip('Lighting On')
        self._toolBarLightingOn.setIcon(self._icons['lighting-on'])
        self._toolBarLightingOn.setCheckable(True)
        self._toolBarLightingOn.setChecked(True)
        self._toolBarLighting.addAction(self._toolBarLightingOn)

        # tool bar (lighting) > off
        self._toolBarLightingOff: QAction = QAction(self._toolBarLighting)
        self._toolBarLightingOff.setToolTip('Lighting Off')
        self._toolBarLightingOff.setIcon(self._icons['lighting-off'])
        self._toolBarLightingOff.setCheckable(True)
        self._toolBarLighting.addAction(self._toolBarLightingOff)

        # tool bar (interaction)
        self._toolBarInteraction: QToolBar = QToolBar(self)
        self._toolBarInteraction.setFloatable(False)
        self.addToolBar(self._toolBarInteraction)

        # tool bar (interaction) > rotate
        self._toolBarInteractionRotate: QAction = QAction(self._toolBarInteraction)
        self._toolBarInteractionRotate.setToolTip('Rotate (Hold Shift to Spin)')
        self._toolBarInteractionRotate.setIcon(self._icons['interaction-style-rotate'])
        self._toolBarInteractionRotate.setCheckable(True)
        self._toolBarInteractionRotate.setChecked(True)
        self._toolBarInteraction.addAction(self._toolBarInteractionRotate)

        # tool bar (interaction) > pan
        self._toolBarInteractionPan: QAction = QAction(self._toolBarInteraction)
        self._toolBarInteractionPan.setToolTip('Pan')
        self._toolBarInteractionPan.setIcon(self._icons['interaction-style-pan'])
        self._toolBarInteractionPan.setCheckable(True)
        self._toolBarInteraction.addAction(self._toolBarInteractionPan)

        # tool bar (interaction) > zoom
        self._toolBarInteractionZoom: QAction = QAction(self._toolBarInteraction)
        self._toolBarInteractionZoom.setToolTip('Zoom')
        self._toolBarInteractionZoom.setIcon(self._icons['interaction-style-zoom'])
        self._toolBarInteractionZoom.setCheckable(True)
        self._toolBarInteraction.addAction(self._toolBarInteractionZoom)

        # tool bar (interaction) > pick single
        self._toolBarInteractionPickSingle: QAction = QAction(self._toolBarInteraction)
        self._toolBarInteractionPickSingle.setToolTip('Pick Single (Hold Shift to Unpick)')
        self._toolBarInteractionPickSingle.setIcon(self._icons['interaction-style-pick-single'])
        self._toolBarInteractionPickSingle.setCheckable(True)
        self._toolBarInteractionPickSingle.setEnabled(False)
        self._toolBarInteraction.addAction(self._toolBarInteractionPickSingle)

        # tool bar (interaction) > pick multiple
        self._toolBarInteractionPickMultiple: QAction = QAction(self._toolBarInteraction)
        self._toolBarInteractionPickMultiple.setToolTip('Pick Multiple (Hold Shift to Unpick)')
        self._toolBarInteractionPickMultiple.setIcon(self._icons['interaction-style-pick-multiple'])
        self._toolBarInteractionPickMultiple.setCheckable(True)
        self._toolBarInteractionPickMultiple.setEnabled(False)
        self._toolBarInteraction.addAction(self._toolBarInteractionPickMultiple)

        # tool bar (interaction) > probe
        self._toolBarInteractionProbe: QAction = QAction(self._toolBarInteraction)
        self._toolBarInteractionProbe.setToolTip('Probe Node/Element')
        self._toolBarInteractionProbe.setIcon(self._icons['interaction-style-probe'])
        self._toolBarInteractionProbe.setCheckable(True)
        self._toolBarInteraction.addAction(self._toolBarInteractionProbe)

        # tool bar (interaction) > ruler
        self._toolBarInteractionRuler: QAction = QAction(self._toolBarInteraction)
        self._toolBarInteractionRuler.setToolTip('Measure Distance')
        self._toolBarInteractionRuler.setIcon(self._icons['interaction-style-ruler'])
        self._toolBarInteractionRuler.setCheckable(True)
        self._toolBarInteraction.addAction(self._toolBarInteractionRuler)

        # central widget
        self._centralWidget: QWidget = QWidget(self)
        self.setCentralWidget(self._centralWidget)

        # central widget layout
        self._centralWidgetLayout: QVBoxLayout = QVBoxLayout(self._centralWidget)
        self._centralWidget.setLayout(self._centralWidgetLayout)

        # vertical splitter
        self._verticalSplitter: QSplitter = QSplitter(self._centralWidget)
        self._verticalSplitter.setHandleWidth(9)
        self._verticalSplitter.setOrientation(Qt.Orientation.Vertical)
        self._centralWidgetLayout.addWidget(self._verticalSplitter)

        # size policy
        sizePolicy0: QSizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy0.setVerticalStretch(1)

        # horizontal splitter
        self._horizontalSplitter: QSplitter = QSplitter(self._verticalSplitter)
        self._horizontalSplitter.setHandleWidth(9)
        self._horizontalSplitter.setOrientation(Qt.Orientation.Horizontal)
        self._horizontalSplitter.setSizePolicy(sizePolicy0)
        self._verticalSplitter.addWidget(self._horizontalSplitter)

        # splitter left
        self._splitterLeft: QFrame = QFrame(self._horizontalSplitter)
        self._splitterLeft.resize(410, 0)
        self._horizontalSplitter.addWidget(self._splitterLeft)

        # splitter left layout
        self._splitterLeftLayout: QVBoxLayout = QVBoxLayout(self._splitterLeft)
        self._splitterLeftLayout.setContentsMargins(0, 0, 0, 0)
        self._splitterLeftLayout.setSpacing(0)
        self._splitterLeft.setLayout(self._splitterLeftLayout)

        # model tree
        self._modelTree: ModelDatabaseControl = ModelDatabaseControl(self._splitterLeft)
        self._modelTree.setColumnWidth(0, 250)
        self._modelTree.setColumnWidth(1, 150)
        self._splitterLeftLayout.addWidget(self._modelTree)

        # output tree
        self._outputTree: OutputDatabaseControl = OutputDatabaseControl(self._splitterLeft)
        self._outputTree.setVisible(False)
        self._splitterLeftLayout.addWidget(self._outputTree)

        # terminal
        self._terminal: Terminal = Terminal(self._verticalSplitter)
        self._verticalSplitter.addWidget(self._terminal)

        # size policy
        sizePolicy1: QSizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(1)

        # right splitter
        self._rightSplitter: QFrame = QFrame(self._horizontalSplitter)
        self._rightSplitter.setSizePolicy(sizePolicy1)
        self._horizontalSplitter.addWidget(self._rightSplitter)

        # right splitter layout
        self._rightSplitterLayout: QVBoxLayout = QVBoxLayout(self._rightSplitter)
        self._rightSplitterLayout.setContentsMargins(0, 0, 0, 0)
        self._rightSplitterLayout.setSpacing(0)
        self._rightSplitter.setLayout(self._rightSplitterLayout)

        # model viewport
        self._modelViewport: Viewport = Viewport(self._rightSplitter)
        self._rightSplitterLayout.addWidget(self._modelViewport)

        # output viewport
        self._outputViewport: Viewport = Viewport(self._rightSplitter)
        self._outputViewport.setVisible(False)
        self._rightSplitterLayout.addWidget(self._outputViewport)

        # dialogs
        self._solverDialog: SolverDialog = SolverDialog(self)
        self._optionsCommonDialog: OptionsCommonDialog = OptionsCommonDialog(self)
