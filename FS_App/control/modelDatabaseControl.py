from typing import cast
from dataModel import ModelDatabase, DataObject, ModelingSpaces
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
    __slots__ = ('_rootItem', '_modelDatabase')

    def __init__(self, parent: QWidget) -> None:
        '''Model database control constructor.'''
        super().__init__(parent)
        self._modelDatabase: ModelDatabase | None = None

        # load style sheet from file
        with open('./resources/style/tree-control.qss', 'r') as file:
            styleSheet: str = file.read()

        # tree widget setup
        self.setColumnCount(2)
        self.setHeaderLabels(('Property', 'Value'))
        self.header().setSectionsMovable(False)
        self.setAlternatingRowColors(True)
        self.setStyleSheet(styleSheet)
        self.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.customContextMenuRequested.connect(self.launchContextMenu) # type: ignore

        # root item
        self._rootItem: QTreeWidgetItem = QTreeWidgetItem(self.invisibleRootItem(), ('Model Database (Empty)',))

    def launchContextMenu(self) -> None:
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

    def nodeSetControlConstructor(self, parent: QTreeWidgetItem, name: str) -> DataObjectControl:
        '''Returns a new node set control.'''
        if not self._modelDatabase: raise RuntimeError('a model database is required')
        control = DataObjectControl(parent, self._modelDatabase.nodeSets[name])
        control.newField('count', ('Node Count',), 'LineEdit', readOnly=True)
        return control

    def elementSetControlConstructor(self, parent: QTreeWidgetItem, name: str) -> DataObjectControl:
        '''Returns a new element set control.'''
        if not self._modelDatabase: raise RuntimeError('a model database is required')
        control = DataObjectControl(parent, self._modelDatabase.elementSets[name])
        control.newField('count', ('Element Count',), 'LineEdit', readOnly=True)
        return control

    def materialControlConstructor(self, parent: QTreeWidgetItem, name: str) -> DataObjectControl:
        '''Returns a new material control.'''
        if not self._modelDatabase: raise RuntimeError('a model database is required')
        control = DataObjectControl(parent, self._modelDatabase.materials[name])
        control.newField('young', ('Mechanical Properties', "Young's Modulus"), 'LineEdit')
        control.newField('poisson', ('Mechanical Properties', "Poisson's Ratio"), 'LineEdit')
        control.newField('density', ('General Properties', 'Mass Density'), 'LineEdit')
        return control

    def sectionControlConstructor(self, parent: QTreeWidgetItem, name: str) -> DataObjectControl:
        '''Returns a new section control.'''
        if not self._modelDatabase: raise RuntimeError('a model database is required')
        control = DataObjectControl(parent, self._modelDatabase.sections[name])
        control.newField('elementSetName', ('Element Set',), 'ComboBox', self._modelDatabase.elementSets)
        control.newField('materialName', ('Material',), 'ComboBox', self._modelDatabase.materials)
        control.newField('stressState', ('Stress State',), 'ComboBox', self._modelDatabase.stressStates)
        if self._modelDatabase.mesh.modelingSpace == ModelingSpaces.TwoDimensional:
            control.newField('planeThickness', ('Plane Thickness',), 'LineEdit')
        return control

    def concentratedLoadControlConstructor(self, parent: QTreeWidgetItem, name: str) -> DataObjectControl:
        '''Returns a new concentrated load control.'''
        if not self._modelDatabase: raise RuntimeError('a model database is required')
        control = DataObjectControl(parent, self._modelDatabase.concentratedLoads[name])
        control.newField('nodeSetName', ('Node Set',), 'ComboBox', self._modelDatabase.nodeSets)
        control.newField('x', ('Components', 'X'), 'LineEdit')
        control.newField('y', ('Components', 'Y'), 'LineEdit')
        if self._modelDatabase.mesh.modelingSpace == ModelingSpaces.ThreeDimensional:
            control.newField('z', ('Components', 'Z'), 'LineEdit')
        return control

    def boundaryConditionControlConstructor(self, parent: QTreeWidgetItem, name: str) -> DataObjectControl:
        '''Returns a new boundary condition control.'''
        if not self._modelDatabase: raise RuntimeError('a model database is required')
        control = DataObjectControl(parent, self._modelDatabase.boundaryConditions[name])
        control.newField('nodeSetName', ('Node Set',), 'ComboBox', self._modelDatabase.nodeSets)
        control.newField('isActiveInX', ('Active DOFs', 'X'), 'CheckBox')
        control.newField('isActiveInY', ('Active DOFs', 'Y'), 'CheckBox')
        control.newField('x', ('Components', 'X'), 'LineEdit')
        control.newField('y', ('Components', 'Y'), 'LineEdit')
        if self._modelDatabase.mesh.modelingSpace == ModelingSpaces.ThreeDimensional:
            control.newField('isActiveInZ', ('Active DOFs', 'Z'), 'CheckBox')
            control.newField('z', ('Components', 'Z'), 'LineEdit')
        return control

    def setModelDatabase(self, modelDatabase: ModelDatabase | None) -> None:
        '''Builds the model database tree widget based on the specified model database.'''
        # detach from previous model database
        self.detach()
        # build new tree
        self._modelDatabase = modelDatabase
        if self._modelDatabase:
            DataObjectContainerControl(
                self._rootItem, self._modelDatabase.nodeSets, self.nodeSetControlConstructor
            )
            DataObjectContainerControl(
                self._rootItem, self._modelDatabase.elementSets, self.elementSetControlConstructor
            )
            DataObjectContainerControl(
                self._rootItem, self._modelDatabase.materials, self.materialControlConstructor
            )
            DataObjectContainerControl(
                self._rootItem, self._modelDatabase.sections, self.sectionControlConstructor
            )
            DataObjectContainerControl(
                self._rootItem, self._modelDatabase.concentratedLoads, self.concentratedLoadControlConstructor
            )
            DataObjectContainerControl(
                self._rootItem, self._modelDatabase.boundaryConditions, self.boundaryConditionControlConstructor
            )
            self._rootItem.setText(0, self._modelDatabase.name)
            self._rootItem.setExpanded(True)

    def detach(self) -> None:
        '''
        Deregister all callbacks and disconnect all signals.
        This method should be called prior to object deletion.
        Not calling this method may prevent object deletion.
        '''
        self._modelDatabase = None
        for i in range(self._rootItem.childCount() - 1, -1, -1):
            cast(DataObjectContainerControl, self._rootItem.child(i)).detach()
            self._rootItem.removeChild(self._rootItem.child(i))
        self._rootItem.setText(0, 'Model Database (Empty)')

    def currentDataObject(self) -> DataObject | None:
        '''Gets the currently selected data object.'''
        item: QTreeWidgetItem = self.currentItem()
        while item != self._rootItem:
            if isinstance(item, DataObjectControl):
                return item.dataObject
            item = item.parent()
        return None
