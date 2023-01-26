from typing import cast
from dataModel import ModelDatabase
from control.dataObjectControl import DataObjectControl
from control.dataObjectContainerControl import DataObjectContainerControl
from PySide6.QtWidgets import QWidget, QTreeWidget, QTreeWidgetItem, QMenu
from PySide6.QtGui import Qt, QCursor, QIcon, QAction
from PySide6.QtCore import QMetaObject

class ModelDatabaseControl(QTreeWidget):
    '''
    Control for model databases.
    Builds the model database tree widget.
    '''

    # attribute slots
    __slots__ = ('_modelDatabase',)

    def __init__(self, parent: QWidget, modelDatabase: ModelDatabase | None = None) -> None:
        '''Model database control constructor.'''
        super().__init__(parent)
        self._modelDatabase: ModelDatabase | None = None

        # load style sheet from file
        with open('./resources/style/model-database-control.qss', 'r') as file:
            styleSheet: str = file.read()

        # tree widget setup
        self.setColumnCount(2)
        self.setHeaderLabels(('Property', 'Value'))
        self.header().setSectionsMovable(False)
        self.setAlternatingRowColors(True)
        self.setStyleSheet(styleSheet)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self._launchContextMenu) # type: ignore

        # connect to model database
        if modelDatabase: self.setModelDatabase(modelDatabase)
        else: self.detach()

    def _launchContextMenu(self) -> None:
        '''Launches the context menu.'''
        currentItem: QTreeWidgetItem = self.currentItem()
        match currentItem:
            case DataObjectContainerControl():
                icon: QIcon = QIcon('./resources/images/add.svg')
                menu: QMenu = QMenu(self)
                action: QAction = menu.addAction('Add') # type: ignore
                action.setIcon(icon)
                connection: QMetaObject.Connection = action.triggered.connect( # type: ignore
                    lambda: currentItem.container.new()
                )
            case DataObjectControl():
                parentItem: DataObjectContainerControl = cast(DataObjectContainerControl, currentItem.parent())
                icon: QIcon = QIcon('./resources/images/remove.svg')
                menu: QMenu = QMenu(self)
                action: QAction = menu.addAction('Remove') # type: ignore
                action.setIcon(icon)
                connection: QMetaObject.Connection = action.triggered.connect( # type: ignore
                    lambda: parentItem.container.__delitem__(currentItem.dataObject.name)
                )
            case _: return
        menu.exec(QCursor.pos())
        menu.disconnect(connection) # type: ignore

    def _materialControlConstructor(self, parent: QTreeWidgetItem, name: str) -> DataObjectControl:
        '''Returns a new material control.'''
        if not self._modelDatabase: raise RuntimeError('a model database is required')
        control = DataObjectControl(parent, self._modelDatabase.materials[name])
        control.newField('young', ('Mechanical Properties', "Young's Modulus"), 'LineEdit')
        control.newField('poisson', ('Mechanical Properties', "Poisson's Ratio"), 'LineEdit')
        control.newField('density', ('General Properties', 'Mass Density'), 'LineEdit')
        return control

    def _sectionControlConstructor(self, parent: QTreeWidgetItem, name: str) -> DataObjectControl:
        '''Returns a new section control.'''
        if not self._modelDatabase: raise RuntimeError('a model database is required')
        control = DataObjectControl(parent, self._modelDatabase.sections[name])
        control.newField('materialName', ('Material',), 'ComboBox', self._modelDatabase.materials)
        control.newField('stressState', ('Stress State',), 'ComboBox', self._modelDatabase.stressStates)
        control.newField('planeThickness', ('Plane Thickness',), 'LineEdit')
        return control

    def setModelDatabase(self, modelDatabase: ModelDatabase) -> None:
        '''Builds the model database tree widget based on the specified model database.'''
        self.detach()
        self.clear()
        self._modelDatabase = modelDatabase

        # create children
        parent: QTreeWidgetItem = QTreeWidgetItem(self.invisibleRootItem(), (self._modelDatabase.name,))
        DataObjectContainerControl(parent, self._modelDatabase.materials, self._materialControlConstructor)
        DataObjectContainerControl(parent, self._modelDatabase.sections, self._sectionControlConstructor)
        parent.setExpanded(True)

    def detach(self) -> None:
        '''
        Deregister all callbacks and disconnect all signals.
        This method should be called prior to object deletion.
        Not calling this method may prevent object deletion.
        '''
        self._modelDatabase = None
        parent: QTreeWidgetItem | None = self.invisibleRootItem().child(0)

        if parent:
            for i in range(parent.childCount()):
                cast(DataObjectContainerControl, parent.child(i)).detach()
            self.clear()
        QTreeWidgetItem(self.invisibleRootItem(), ('Model Database (Empty)',))
