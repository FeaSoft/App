from collections.abc import Callable
from dataModel.dataObject import DataObject

class SurfaceTraction(DataObject):
    '''
    Definition of a surface traction.
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
    def x(self) -> float:
        '''Surface traction component in the x-direction.'''
        return self._x

    @x.setter
    def x(self, value: float) -> None:
        '''Surface traction component in the x-direction (setter).'''
        self._x = value
        self.notifyPropertyChanged('x')

    @property
    def y(self) -> float:
        '''Surface traction component in the y-direction.'''
        return self._y

    @y.setter
    def y(self, value: float) -> None:
        '''Surface traction component in the y-direction (setter).'''
        self._y = value
        self.notifyPropertyChanged('y')

    @property
    def z(self) -> float:
        '''Surface traction component in the z-direction.'''
        return self._z

    @z.setter
    def z(self, value: float) -> None:
        '''Surface traction component in the z-direction (setter).'''
        self._z = value
        self.notifyPropertyChanged('z')

    # attribute slots
    __slots__ = ('_surfaceSetName', '_x', '_y', '_z')

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
        self._x: float = 0.0
        self._y: float = 0.0
        self._z: float = 0.0

    def components(self) -> tuple[float, float, float]:
        '''Returns the concentrated load components.'''
        return (self._x, self._y, self._z)
