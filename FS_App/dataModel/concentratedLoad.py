from collections.abc import Callable
from dataModel.dataObject import DataObject

class ConcentratedLoad(DataObject):
    '''
    Definition of a concentrated load.
    '''

    @property
    def nodeSetName(self) -> str:
        '''Name of the associated node set.'''
        return self._nodeSetName

    @nodeSetName.setter
    def nodeSetName(self, value: str) -> None:
        '''Name of the associated node set (setter).'''
        self._nodeSetName = value
        self.notifyPropertyChanged('nodeSetName')

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
    __slots__ = ('_nodeSetName', '_x', '_y', '_z')

    def __init__(
        self,
        nameGetter: Callable[[DataObject], str],
        nameSetter: Callable[[DataObject, str], None],
        isAssignedGetter: Callable[[DataObject], bool]
    ) -> None:
        '''Concentrated load constructor.'''
        super().__init__(nameGetter, nameSetter, isAssignedGetter)
        self._nodeSetName: str = '<Undefined>'
        self._x: float = 0.0
        self._y: float = 0.0
        self._z: float = 0.0

    def components(self) -> tuple[float, float, float]:
        '''Returns the concentrated load components.'''
        return (self._x, self._y, self._z)
