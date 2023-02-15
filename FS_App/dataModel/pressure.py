from collections.abc import Callable
from dataModel.dataObject import DataObject

class Pressure(DataObject):
    '''
    Definition of a pressure.
    '''

    @property
    def surfaceSetName(self) -> str:
        '''Name of the associated surface set.'''
        return self._surfaceSetName

    @surfaceSetName.setter
    def surfaceSetName(self, value: str) -> None:
        '''Name of the associated surface set (setter).'''
        self._surfaceSetName = value
        self.notifyPropertyChanged('surfaceSetName')

    @property
    def magnitude(self) -> float:
        '''Pressure magnitude.'''
        return self._magnitude

    @magnitude.setter
    def magnitude(self, value: float) -> None:
        '''Pressure magnitude (setter).'''
        self._magnitude = value
        self.notifyPropertyChanged('magnitude')

    # attribute slots
    __slots__ = ('_surfaceSetName', '_magnitude')

    def __init__(
        self,
        indexGetter: Callable[[DataObject], int],
        nameGetter: Callable[[DataObject], str],
        nameSetter: Callable[[DataObject, str], None],
        isAssignedGetter: Callable[[DataObject], bool]
    ) -> None:
        '''Surface load constructor.'''
        super().__init__(indexGetter, nameGetter, nameSetter, isAssignedGetter)
        self._surfaceSetName: str = '<Undefined>'
        self._magnitude: float = 0.0
