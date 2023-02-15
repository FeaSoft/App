from collections.abc import Callable
from dataModel.dataObject import DataObject

class BoundaryCondition(DataObject):
    '''
    Definition of a boundary condition (prescribed displacements).
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

    @property
    def isActiveInX(self) -> bool:
        '''Determines if the boundary condition is active in the x-direction.'''
        return self._isActiveInX

    @isActiveInX.setter
    def isActiveInX(self, value: bool) -> None:
        '''Determines if the boundary condition is active in the x-direction (setter).'''
        self._isActiveInX = value
        self.notifyPropertyChanged('isActiveInX')

    @property
    def isActiveInY(self) -> bool:
        '''Determines if the boundary condition is active in the y-direction.'''
        return self._isActiveInY

    @isActiveInY.setter
    def isActiveInY(self, value: bool) -> None:
        '''Determines if the boundary condition is active in the y-direction (setter).'''
        self._isActiveInY = value
        self.notifyPropertyChanged('isActiveInY')

    @property
    def isActiveInZ(self) -> bool:
        '''Determines if the boundary condition is active in the z-direction.'''
        return self._isActiveInZ

    @isActiveInZ.setter
    def isActiveInZ(self, value: bool) -> None:
        '''Determines if the boundary condition is active in the z-direction (setter).'''
        self._isActiveInZ = value
        self.notifyPropertyChanged('isActiveInZ')

    # attribute slots
    __slots__ = ('_nodeSetName', '_x', '_y', '_z', '_isActiveInX', '_isActiveInY', '_isActiveInZ')

    def __init__(
        self,
        indexGetter: Callable[[DataObject], int],
        nameGetter: Callable[[DataObject], str],
        nameSetter: Callable[[DataObject, str], None],
        isAssignedGetter: Callable[[DataObject], bool]
    ) -> None:
        '''Concentrated load constructor.'''
        super().__init__(indexGetter, nameGetter, nameSetter, isAssignedGetter)
        self._nodeSetName: str = '<Undefined>'
        self._x: float = 0.0
        self._y: float = 0.0
        self._z: float = 0.0
        self._isActiveInX: bool = False
        self._isActiveInY: bool = False
        self._isActiveInZ: bool = False

    def components(self) -> tuple[float, float, float]:
        '''Returns the boundary condition components.'''
        return (self._x, self._y, self._z)

    def activeDOFs(self) -> tuple[bool, bool, bool]:
        '''Returns the boundary condition active degrees of freedom.'''
        return (self._isActiveInX, self._isActiveInY, self._isActiveInZ)
