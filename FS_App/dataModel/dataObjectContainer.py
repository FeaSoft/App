from typing import Type
from collections.abc import Callable
from string import ascii_letters, digits, whitespace
from dataModel.dataObject import DataObject

class DataObjectContainer:
    '''
    A container that holds data objects.
    It is through the container that data objects are created and deleted.
    '''

    @property
    def name(self) -> str:
        '''Data object container name.'''
        return self._name

    # attribute slots
    __slots__ = ('_dataObjectType', '_name', '_prefix', '_names', '_dataObjects', '_callbacks')

    def __init__(self, dataObjectType: Type[DataObject], name: str, prefix: str) -> None:
        '''Data object container constructor.'''
        self._dataObjectType: Type[DataObject] = dataObjectType
        self._name: str = name
        self._prefix: str = prefix
        self._names: list[str] = []
        self._dataObjects: list[DataObject] = []
        self._callbacks: dict[int, Callable[[str | None, str | None], None]] = {}

    def __len__(self) -> int:
        '''Return len(self).'''
        return self._dataObjects.__len__()

    def __getitem__(self, name: str) -> DataObject:
        '''Get the data object with the specified name.'''
        return self._dataObjects[self._names.index(name)]

    def __delitem__(self, name: str) -> None:
        '''Delete the data object with the specified name.'''
        index: int = self._names.index(name)
        del self._names[index]
        del self._dataObjects[index]
        self.notifyContainerChanged(oldName=name)

    def generateUniqueName(self) -> str:
        '''Generates a unique data object name.'''
        i: int = len(self._names) + 1
        while self._prefix + str(i) in self._names: i += 1
        return self._prefix + str(i)

    def validateNewName(self, dataObject: DataObject, newName: str) -> None:
        '''Raises a ValueError if the new data object name is not valid.'''
        # check for empty string
        if newName == '':
            raise ValueError('name is empty')

        # check for whitespaces
        for c in whitespace:
            if c in newName:
                raise ValueError('name contains whitespaces')

        # check for invalid characters
        for c in newName:
            if c not in ascii_letters + digits + '-_.':
                raise ValueError(f"name contains invalid character: '{c}'")

        # check for name already in use
        if newName in self._names and self[newName] != dataObject:
            raise ValueError('name is already in use')

    def findName(self, dataObject: DataObject) -> str:
        '''Returns the name of the specified data object.'''
        return self._names[self._dataObjects.index(dataObject)]

    def changeName(self, dataObject: DataObject, newName: str) -> None:
        '''Changes the name of the specified data object.'''
        self.validateNewName(dataObject, newName)
        index: int = self._dataObjects.index(dataObject)
        oldName: str = self._names[index]
        self._names[index] = newName
        self.notifyContainerChanged(oldName, newName)

    def notifyContainerChanged(self, oldName: str | None = None, newName: str | None = None) -> None:
        '''This method is called when an item is added to or removed from the container.'''
        for callback in self._callbacks.values(): callback(oldName, newName)

    def registerCallback(self, callback: Callable[[str | None, str | None], None]) -> int:
        '''
        Adds the specified callback function to the internal container of callbacks.
        Returns a key used to deregister the callback.
        '''
        key: int = 0
        while key in self._callbacks: key += 1
        self._callbacks[key] = callback
        return key

    def deregisterCallback(self, key: int) -> None:
        '''Removes the callback function from the internal container of callbacks using its key.'''
        del self._callbacks[key]

    def names(self) -> tuple[str, ...]:
        '''Returns a tuple with the data object names.'''
        return tuple(self._names)

    def new(self) -> None:
        '''Creates a new default instance of a data object and adds it to the container.'''
        newName: str = self.generateUniqueName()
        newDataObject: DataObject = self._dataObjectType(self.findName, self.changeName)
        self._names.append(newName)
        self._dataObjects.append(newDataObject)
        self.notifyContainerChanged(newName=newName)
