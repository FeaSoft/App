from typing import Literal
from collections.abc import Callable
from dataModel.dataObject import DataObject

class BodyLoad(DataObject):
    '''
    Definition of a body load.
    '''

    @property
    def elementSetName(self) -> str:
        '''Name of the associated element set.'''
        return self._elementSetName

    @elementSetName.setter
    def elementSetName(self, value: str) -> None:
        '''Name of the associated element set (setter).'''
        self._elementSetName = value
        self.notifyPropertyChanged('elementSetName')

    @property
    def type(self) -> Literal['<Undefined>', 'Acceleration', 'Body Force']:
        '''Type of the body load.'''
        return self._type

    @type.setter
    def type(self, value: Literal['<Undefined>', 'Acceleration', 'Body Force']) -> None:
        '''Type of the body load (setter).'''
        self._type = value
        self.notifyPropertyChanged('type')

    @property
    def x(self) -> float:
        '''Load component in the x-direction.'''
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        '''Load component in the x-direction (setter).'''
        self._x = value
        self.notifyPropertyChanged('x')

    @property
    def y(self) -> float:
        '''Load component in the y-direction.'''
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        '''Load component in the y-direction (setter).'''
        self._y = value
        self.notifyPropertyChanged('y')

    @property
    def z(self) -> float:
        '''Load component in the z-direction.'''
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        '''Load component in the z-direction (setter).'''
        self._z = value
        self.notifyPropertyChanged('z')

    # attribute slots
    __slots__ = ('_elementSetName', '_type', '_x', '_y', '_z')

    def __init__(
        self,
        indexGetter: Callable[[DataObject], int],
        nameGetter: Callable[[DataObject], str],
        nameSetter: Callable[[DataObject, str], None],
        isAssignedGetter: Callable[[DataObject], bool]
    ) -> None:
        '''Body load constructor.'''
        super().__init__(indexGetter, nameGetter, nameSetter, isAssignedGetter)
        self._elementSetName: str = '<Undefined>'
        self._type: Literal['<Undefined>', 'Acceleration', 'Body Force'] = '<Undefined>'
        self._x: float = 0.0
        self._y: float = 0.0
        self._z: float = 0.0

    def components(self) -> tuple[float, float, float]:
        '''Returns the body load components.'''
        return (self._x, self._y, self._z)
