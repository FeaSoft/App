from dataModel import OutputDatabase
from PySide6.QtWidgets import QWidget, QTreeWidget, QTreeWidgetItem

class OutputDatabaseControl(QTreeWidget):
    '''
    Control for output databases.
    Builds the output database tree widget.
    '''

    # attribute slots
    __slots__ = ('_rootItem', '_outputDatabase')

    def __init__(self, parent: QWidget) -> None:
        '''Output database control constructor.'''
        super().__init__(parent)
        self._outputDatabase: OutputDatabase | None = None

        # load style sheet from file
        with open('./resources/style/tree-control.qss', 'r') as file:
            styleSheet: str = file.read()

        # tree widget setup
        self.setColumnCount(1)
        self.setHeaderHidden(True)
        self.setAlternatingRowColors(True)
        self.setStyleSheet(styleSheet)

        # root item
        self._rootItem: QTreeWidgetItem = QTreeWidgetItem(self.invisibleRootItem(), ('Output Database (Empty)',))

    def clear(self) -> None:
        '''Clears the tree widget items.'''
        self._outputDatabase = None
        for i in range(self._rootItem.childCount() - 1, -1, -1):
            self._rootItem.removeChild(self._rootItem.child(i))
        self._rootItem.setText(0, 'Output Database (Empty)')

    def setOutputDatabase(self, outputDatabase: OutputDatabase | None) -> None:
        '''Builds the output database tree widget based on the specified output database.'''
        # clear previous output database
        self.clear()
        # build new tree
        self._outputDatabase = outputDatabase
        if self._outputDatabase:
            for frame in self._outputDatabase.frameNumbers():
                frameItem: QTreeWidgetItem = QTreeWidgetItem(self._rootItem, (f'Frame {frame}',))
                for groupName in self._outputDatabase.nodalScalarFieldGroupNames(frame):
                    groupItem: QTreeWidgetItem = QTreeWidgetItem(frameItem, (groupName,))
                    for fieldName in self._outputDatabase.nodalScalarFieldNames(frame, groupName):
                        QTreeWidgetItem(groupItem, (fieldName,))
            self._rootItem.setText(0, 'Output Database')
            self._rootItem.setExpanded(True)

    def currentSelection(self) -> tuple[int, str, str] | None:
        '''Gets the currently selected nodal scalar field.'''
        if not self._outputDatabase: return None
        # get current item depth
        depth: int = 0
        item: QTreeWidgetItem = self.currentItem()
        while item != self._rootItem:
            depth += 1
            item = item.parent()
        # return based on depth (if depth == 3: a nodal scalar field is selected)
        if depth == 3:
            frame: int = int(self.currentItem().parent().parent().text(0).split(' ')[1])
            groupName: str = self.currentItem().parent().text(0)
            fieldName: str = self.currentItem().text(0)
            return frame, groupName, fieldName
        return None
