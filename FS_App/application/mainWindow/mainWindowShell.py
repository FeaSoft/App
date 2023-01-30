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
                'file-new', 'view-front', 'view-back', 'view-top', 'view-bottom', 'view-left', 'view-right',
                'view-isometric'
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

        # tool bar (file)
        self._toolBarFile: QToolBar = QToolBar(self)
        self._toolBarFile.setFloatable(False)
        self.addToolBar(self._toolBarFile)

        # tool bar (file) > new
        self._toolBarFileNew: QAction = QAction(self._toolBarFile)
        self._toolBarFileNew.setToolTip('New Model Database')
        self._toolBarFileNew.setIcon(self._icons['file-new'])
        self._toolBarFile.addAction(self._toolBarFileNew)

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