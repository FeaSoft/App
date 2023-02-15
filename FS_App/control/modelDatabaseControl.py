from typing import cast
from dataModel import ModelDatabase, DataObject, ModelingSpaces, NodeSet, SurfaceSet
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
        connection:  QMetaObject.Connection | None = None
        connection0: QMetaObject.Connection | None = None
        currentItem: QTreeWidgetItem = self.currentItem()
        match currentItem:
            case DataObjectContainerControl():
                icon: QIcon = QIcon('./resources/images/add.svg')
                menu: QMenu = QMenu(self)
                action: QAction = menu.addAction('Add') # type: ignore
                action.setIcon(icon)
                connection = action.triggered.connect(lambda: currentItem.container.new()) # type: ignore
            case DataObjectControl():
                parentItem: DataObjectContainerControl = cast(DataObjectContainerControl, currentItem.parent())
                menu: QMenu = QMenu(self)
                if isinstance(currentItem.dataObject, NodeSet):
                    action0: QAction = menu.addAction('Convert to Surface Set') # type: ignore
                    action0.setIcon(QIcon('./resources/images/convert.svg'))
                    def _lambda() -> None:
                        if not self._modelDatabase: return
                        nodeSet: NodeSet = cast(NodeSet, currentItem.dataObject)
                        surfaceSet: SurfaceSet = cast(SurfaceSet, self._modelDatabase.surfaceSets.new())
                        surfaceSet.add(self._modelDatabase.convertNodeIndicesToSurfaces(nodeSet.indices()))
                    connection0 = action0.triggered.connect(_lambda) # type: ignore
                elif isinstance(currentItem.dataObject, SurfaceSet):
                    action0: QAction = menu.addAction('Flip Normals') # type: ignore
                    action0.setIcon(QIcon('./resources/images/convert.svg'))
                    def _lambda() -> None:
                        surfaceSet: SurfaceSet = cast(SurfaceSet, currentItem.dataObject)
                        surfaceSet.flipNormals()
                        # trick for re-plotting arrows
                        self.setCurrentItem(self._rootItem)
                        self.setCurrentItem(currentItem)
                    connection0 = action0.triggered.connect(_lambda) # type: ignore
                action: QAction = menu.addAction('Remove') # type: ignore
                action.setIcon(QIcon('./resources/images/remove.svg'))
                connection = action.triggered.connect( # type: ignore
                    lambda: parentItem.container.__delitem__(currentItem.dataObject.name)
                )
            case _: return
        menu.exec(QCursor.pos())
        if connection:  menu.disconnect(connection)  # type: ignore
        if connection0: menu.disconnect(connection0) # type: ignore

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

    def surfaceSetControlConstructor(self, parent: QTreeWidgetItem, name: str) -> DataObjectControl:
        '''Returns a new surface set control.'''
        if not self._modelDatabase: raise RuntimeError('a model database is required')
        control = DataObjectControl(parent, self._modelDatabase.surfaceSets[name])
        control.newField('count', ('Surface Count',), 'LineEdit', readOnly=True)
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

    def pressureControlConstructor(self, parent: QTreeWidgetItem, name: str) -> DataObjectControl:
        '''Returns a new pressure control.'''
        if not self._modelDatabase: raise RuntimeError('a model database is required')
        control = DataObjectControl(parent, self._modelDatabase.pressures[name])
        control.newField('surfaceSetName', ('Surface Set',), 'ComboBox', self._modelDatabase.surfaceSets)
        control.newField('magnitude', ('Magnitude',), 'LineEdit')
        return control

    def surfaceTractionControlConstructor(self, parent: QTreeWidgetItem, name: str) -> DataObjectControl:
        '''Returns a new surface traction control.'''
        if not self._modelDatabase: raise RuntimeError('a model database is required')
        control = DataObjectControl(parent, self._modelDatabase.surfaceTractions[name])
        control.newField('surfaceSetName', ('Surface Set',), 'ComboBox', self._modelDatabase.surfaceSets)
        control.newField('x', ('Components', 'X'), 'LineEdit')
        control.newField('y', ('Components', 'Y'), 'LineEdit')
        if self._modelDatabase.mesh.modelingSpace == ModelingSpaces.ThreeDimensional:
            control.newField('z', ('Components', 'Z'), 'LineEdit')
        return control

    def bodyLoadControlConstructor(self, parent: QTreeWidgetItem, name: str) -> DataObjectControl:
        '''Returns a new body load control.'''
        if not self._modelDatabase: raise RuntimeError('a model database is required')
        control = DataObjectControl(parent, self._modelDatabase.bodyLoads[name])
        control.newField('elementSetName', ('Element Set',), 'ComboBox', self._modelDatabase.elementSets)
        control.newField('type', ('Type',), 'ComboBox', ('Acceleration', 'Body Force'))
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
        self.setCurrentItem(self._rootItem)
        self._modelDatabase = modelDatabase
        if self._modelDatabase:
            DataObjectContainerControl(
                self._rootItem, self._modelDatabase.nodeSets, self.nodeSetControlConstructor
            )
            DataObjectContainerControl(
                self._rootItem, self._modelDatabase.elementSets, self.elementSetControlConstructor
            )
            DataObjectContainerControl(
                self._rootItem, self._modelDatabase.surfaceSets, self.surfaceSetControlConstructor
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
                self._rootItem, self._modelDatabase.pressures, self.pressureControlConstructor
            )
            DataObjectContainerControl(
                self._rootItem, self._modelDatabase.surfaceTractions, self.surfaceTractionControlConstructor
            )
            DataObjectContainerControl(
                self._rootItem, self._modelDatabase.bodyLoads, self.bodyLoadControlConstructor
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
