from abc import ABC, abstractmethod
from collections.abc import Callable

class DataObject(ABC):
    '''
    Abstract base class for generic data objects.
    Model database objects (materials, node sets, etc.) are derived from this class.
    '''

    @property
    def index(self) -> int:
        '''Data object index.'''
        return self._indexGetter(self)

    @property
    def name(self) -> str:
        '''Data object name.'''
        return self._nameGetter(self)

    @name.setter
    def name(self, value: str) -> None:
        '''Data object name (setter).'''
        self._nameSetter(self, value)
        self.notifyPropertyChanged('name')

    @property
    def isAssigned(self) -> bool:
        '''Determines if the data object is currently assigned.'''
        return self._isAssignedGetter(self)

    # attribute slots
    __slots__ = ('_indexGetter', '_nameGetter', '_nameSetter', '_isAssignedGetter', '_callbacks')

    @abstractmethod
    def __init__(
        self,
        indexGetter: Callable[['DataObject'], int],
        nameGetter: Callable[['DataObject'], str],
        nameSetter: Callable[['DataObject', str], None],
        isAssignedGetter: Callable[['DataObject'], bool]
    ) -> None:
        '''Data object constructor.'''
        super().__init__()
        self._indexGetter: Callable[[DataObject], int] = indexGetter
        self._nameGetter: Callable[[DataObject], str] = nameGetter
        self._nameSetter: Callable[[DataObject, str], None] = nameSetter
        self._isAssignedGetter: Callable[[DataObject], bool] = isAssignedGetter
        self._callbacks: dict[int, Callable[[str], None]] = {}

    def notifyPropertyChanged(self, propertyName: str) -> None:
        '''This method is called when a property has changed its value.'''
        for callback in self._callbacks.values(): callback(propertyName)

    def registerCallback(self, callback: Callable[[str], None]) -> int:
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
