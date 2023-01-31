from typing import Any, Literal, cast
from collections.abc import Callable, Sequence
from dataModel import DataObject, DataObjectContainer
from PySide6.QtWidgets import QWidget, QLineEdit, QComboBox, QCheckBox, QTreeWidget, QTreeWidgetItem
from PySide6.QtCore import QMetaObject
from shiboken6 import isValid

class DataObjectControl(QTreeWidgetItem):
    '''
    Control for data objects.
    When data object properties are changed, the data object notifies the control; the control then updates the view.
    When the user inputs changes through the view, it signals the control; the control then updates the data object.
    '''

    @property
    def dataObject(self) -> DataObject:
        '''Controlled data object.'''
        return self._dataObject

    # attribute slots
    __slots__ = (
        '_dataObject', '_callbackKey', '_editWidgets', '_editWidgetConnections', '_itemSources',
        '_itemSourceCallbackKeys'
    )

    def __init__(self, parent: QTreeWidgetItem, dataObject: DataObject) -> None:
        '''Data object control constructor.'''
        super().__init__(parent, (dataObject.name,))
        self._editWidgets: dict[str, QWidget] = {}
        self._editWidgetConnections: dict[str, QMetaObject.Connection] = {}
        self._itemSources: list[DataObjectContainer] = []
        self._itemSourceCallbackKeys: list[int] = []
        self._dataObject: DataObject = dataObject
        self._callbackKey: int = self._dataObject.registerCallback(self.onPropertyChanged)
        self.newField('name', ('Name',), 'LineEdit')

    def onPropertyChanged(self, propertyName: str) -> None:
        '''
        This method is executed once a property of the data object is changed.
        This method makes sure the user sees the actual currently stored information.
        '''
        propertyValue: Any = getattr(self._dataObject, propertyName)
        editWidget: QWidget = self._editWidgets[propertyName]
        if not isValid(editWidget): return

        # update view to show the currently stored property value
        match editWidget:
            case QLineEdit(): editWidget.setText(str(propertyValue))
            case QCheckBox(): editWidget.setChecked(bool(propertyValue))
            case QComboBox(): editWidget.setCurrentText(str(propertyValue))
            case _: raise NotImplementedError('case not implemented')

        # this trick will update the current selection
        self.treeWidget().currentItemChanged.emit( # type: ignore
            self.treeWidget().currentItem(), self.treeWidget().currentItem()
        )

    def onUserEdit(self, propertyName: str) -> None:
        '''
        This method is executed once the user has finished using an edit widget.
        This method makes sure the stored information is updated based on the edit.
        '''
        editWidget: QWidget = self._editWidgets[propertyName]
        if not isValid(editWidget): return

        # do nothing if edit widget is read only
        if isinstance(editWidget, QLineEdit) and editWidget.isReadOnly():
            return

        # get the new user-specified property value (possibly as a string)
        match editWidget:
            case QComboBox(): propertyValue = editWidget.currentText()
            case QCheckBox(): propertyValue = editWidget.isChecked()
            case QLineEdit(): propertyValue = editWidget.text()
            case _: raise NotImplementedError('case not implemented')

        # the try block is used for validation since the user can specify illegal values
        # the except block will raise the exception normally and reset the previous (legal) value
        try:
            match getattr(self._dataObject, propertyName):
                case float(): propertyValue = float(propertyValue)
                case bool(): propertyValue = bool(propertyValue)
                case str(): propertyValue = str(propertyValue)
                case _: raise NotImplementedError('case not implemented')
            setattr(self._dataObject, propertyName, propertyValue)
        except Exception as exception:
            self.onPropertyChanged(propertyName)
            raise exception

    def onItemSourceChanged(self, propertyName: str, oldName: str | None, newName: str | None) -> None:
        '''
        This method is executed once an item is added to or removed from a data object container.
        This method makes sure the combo box items match with the associated data object container.
        '''
        editWidget: QWidget = self._editWidgets[propertyName]
        if not isValid(editWidget): return
        comboBox = cast(QComboBox, editWidget)

        # a name was changed (do not upset current order of items)
        if oldName and newName:
            index = comboBox.findText(oldName)
            comboBox.insertItem(index, newName)
            comboBox.removeItem(index + 1)
            return

        # an item was added or removed
        if newName: comboBox.addItem(newName)
        if oldName: comboBox.removeItem(comboBox.findText(oldName))

    def newField(
        self,
        propertyName: str,
        displayNames: Sequence[str],
        kind: Literal['LineEdit', 'ComboBox', 'CheckBox'],
        itemSource: DataObjectContainer | Sequence[str] | None = None,
        readOnly: bool = False
    ) -> None:
        '''Creates a new editable field in the interface.'''
        if propertyName in self._editWidgets: raise ValueError('property already associated with an existing field')
        propertyValue: Any = getattr(self._dataObject, propertyName)
        treeWidget: QTreeWidget = self.treeWidget()
        if not isValid(treeWidget): return

        # create edit widget callback function
        editWidgetCallback: Callable[[], None] = lambda: self.onUserEdit(propertyName)

        # create edit widget
        match kind:
            case 'LineEdit':
                editWidget = QLineEdit(treeWidget)
                editWidget.setReadOnly(readOnly)
                editWidget.setText(str(propertyValue))
                self._editWidgetConnections[propertyName] = (              # type: ignore
                    editWidget.editingFinished.connect(editWidgetCallback) # type: ignore
                )
            case 'ComboBox':
                editWidget = QComboBox(treeWidget)
                editWidget.addItem('<Undefined>')
                match itemSource:
                    case DataObjectContainer():
                        editWidget.addItems(itemSource.names())
                        itemSourceCallback: Callable[[str | None, str | None], None] = lambda oldName, newName: \
                            self.onItemSourceChanged(propertyName, oldName, newName)
                        itemSourceCallbackKey: int = itemSource.registerCallback(itemSourceCallback)
                        self._itemSources.append(itemSource)
                        self._itemSourceCallbackKeys.append(itemSourceCallbackKey)
                    case Sequence():
                        editWidget.addItems(itemSource)
                    case _: raise NotImplementedError('case not implemented')
                self._editWidgetConnections[propertyName] = (                  # type: ignore
                    editWidget.currentIndexChanged.connect(editWidgetCallback) # type: ignore
                )
            case 'CheckBox':
                editWidget = QCheckBox(treeWidget)
                editWidget.setChecked(bool(propertyValue))
                self._editWidgetConnections[propertyName] = (      # type: ignore
                    editWidget.toggled.connect(editWidgetCallback) # type: ignore
                )
        self._editWidgets[propertyName] = editWidget

        # create subtree and insert edit widget
        parent = self
        for displayName in displayNames:
            if displayName == displayNames[-1]:
                child = QTreeWidgetItem(parent, (displayName,))
                treeWidget.setItemWidget(child, 1, self._editWidgets[propertyName])
            else:
                parentUpdated: bool = False
                for i in range(parent.childCount()):
                    if parent.child(i).text(0) == displayName:
                        parent = parent.child(i)
                        parentUpdated = True
                        break
                if not parentUpdated:
                    parent = QTreeWidgetItem(parent, (displayName,))

    def detach(self) -> None:
        '''
        Deregister all callbacks and disconnect all signals.
        This method should be called prior to object deletion.
        Not calling this method may prevent object deletion.
        '''
        self._dataObject.deregisterCallback(self._callbackKey)
        for propertyName, connection in self._editWidgetConnections.items():
            editWidget: QWidget = self._editWidgets[propertyName]
            if not isValid(editWidget): continue
            editWidget.disconnect(connection) # type: ignore
        for itemSource, itemSourceCallbackKey in zip(self._itemSources, self._itemSourceCallbackKeys):
            itemSource.deregisterCallback(itemSourceCallbackKey)
