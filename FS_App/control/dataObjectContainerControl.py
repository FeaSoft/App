from typing import cast
from collections.abc import Callable
from dataModel import DataObjectContainer
from control.dataObjectControl import DataObjectControl
from PySide6.QtWidgets import QTreeWidgetItem

class DataObjectContainerControl(QTreeWidgetItem):
    '''
    Control for data object containers.
    When data object containers are modified, the container notifies the control; the control then updates the view.
    When the user adds/removes items through the view, it signals the control; the control then updates the container.
    '''

    @property
    def container(self) -> DataObjectContainer:
        '''Controlled data object container.'''
        return self._container

    # attribute slots
    __slots__ = ('_container', '_callbackKey', '_childConstructor')

    def __init__(
        self,
        parent: QTreeWidgetItem,
        container: DataObjectContainer,
        childConstructor: Callable[[QTreeWidgetItem, str], DataObjectControl]
    ) -> None:
        '''Data object container control constructor.'''
        super().__init__(parent, (f'{container.name} [{len(container)}]',))
        self._container: DataObjectContainer = container
        self._callbackKey: int = self._container.registerCallback(self._onContainerChanged)
        self._childConstructor: Callable[[QTreeWidgetItem, str], DataObjectControl] = childConstructor

    def _findChild(self, text: str) -> QTreeWidgetItem:
        '''Find the first child item with the specified text.'''
        for i in range(self.childCount()):
            if self.child(i).text(0) == text:
                return self.child(i)
        raise ValueError('child item not found')

    def _onContainerChanged(self, oldName: str | None, newName: str | None) -> None:
        '''
        This method is executed once an item is added to or removed from a data object container.
        This method makes sure the child items match with the associated data object container.
        '''
        self.setText(0, f'{self._container.name} [{len(self._container)}]')

        # a name was changed (do not upset current order of items)
        if oldName and newName:
            self._findChild(oldName).setText(0, newName)
            return

        # an item was added or removed
        if newName: self._childConstructor(self, newName)
        if oldName:
            child: DataObjectControl = cast(DataObjectControl, self._findChild(oldName))
            child.detach()
            self.removeChild(child)
            del child

    def detach(self) -> None:
        '''
        Deregister all callbacks and disconnect all signals.
        This method should be called prior to object deletion.
        Not calling this method may prevent object deletion.
        '''
        self._container.deregisterCallback(self._callbackKey)
        for i in range(self.childCount()):
            cast(DataObjectControl, self.child(i)).detach()
