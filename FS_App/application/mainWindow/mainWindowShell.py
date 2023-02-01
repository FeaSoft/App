from application.terminal import Terminal
from control import ModelDatabaseControl
from visualization import Viewport
from PySide6.QtGui import Qt, QAction, QIcon
from PySide6.QtWidgets import (
    QWidget, QMainWindow, QMenuBar, QMenu, QToolBar, QVBoxLayout, QSplitter, QSizePolicy, QFrame
)

class MainWindowShell(QMainWindow):
    '''
    The main window shell (basic UI).
    '''

    # attribute slots (not allowed, QT crashes)
    # __slots__ = ...

    def __init__(self) -> None:
        '''Main window shell constructor.'''
        super().__init__()

        # load icons
        self._icons: dict[str, QIcon] = {
            x: QIcon(f'./resources/images/{x}.svg') for x in (
                'file-new', 'file-open', 'file-save', 'file-save-as', 'file-close', 'file-exit', 'view-front',
                'view-back', 'view-top', 'view-bottom', 'view-left', 'view-right', 'view-isometric',
                'interaction-style-rotate', 'interaction-style-pan', 'interaction-style-zoom',
                'interaction-style-pick-single', 'interaction-style-pick-multiple', 'interaction-style-probe',
                'interaction-style-ruler'
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

        # horizontal splitter
        self._horizontalSplitter: QSplitter = QSplitter(self._verticalSplitter)
        self._horizontalSplitter.setHandleWidth(9)
        self._horizontalSplitter.setOrientation(Qt.Orientation.Horizontal)
        sizePolicy0: QSizePolicy = self._horizontalSplitter.sizePolicy()
        sizePolicy0.setVerticalStretch(1)
        self._horizontalSplitter.setSizePolicy(sizePolicy0)
        self._verticalSplitter.addWidget(self._horizontalSplitter)

        # model tree
        self._modelTree: ModelDatabaseControl = ModelDatabaseControl(self._horizontalSplitter)
        self._modelTree.setColumnWidth(0, 250)
        self._modelTree.setColumnWidth(1, 150)
        self._modelTree.resize(410, 0)
        self._horizontalSplitter.addWidget(self._modelTree)

        # terminal
        self._terminal: Terminal = Terminal(self._verticalSplitter)
        self._verticalSplitter.addWidget(self._terminal)

        # viewport frame
        self._viewportFrame: QFrame = QFrame(self._horizontalSplitter)
        self._viewportFrame.setStyleSheet('border: 1px solid rgb(185,185,185);')
        sizePolicy1: QSizePolicy = self._viewportFrame.sizePolicy()
        sizePolicy1.setHorizontalStretch(1)
        self._viewportFrame.setSizePolicy(sizePolicy1)
        self._horizontalSplitter.addWidget(self._viewportFrame)

        # viewport frame layout
        self._viewportFrameLayout: QVBoxLayout = QVBoxLayout(self._viewportFrame)
        self._viewportFrameLayout.setContentsMargins(0, 0, 0, 0)
        self._viewportFrame.setLayout(self._viewportFrameLayout)

        # viewport
        self._viewport: Viewport = Viewport(self._viewportFrame)
        self._viewportFrameLayout.addWidget(self._viewport)
