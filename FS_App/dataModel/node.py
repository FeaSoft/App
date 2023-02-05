class Node:
    '''
    Definition of a finite element node.
    '''

    @property
    def x(self) -> float:
        '''The x-coordinate.'''
        return self._coordinates[0]

    @property
    def y(self) -> float:
        '''The y-coordinate.'''
        return self._coordinates[1]

    @property
    def z(self) -> float:
        '''The z-coordinate.'''
        return self._coordinates[2]

    @property
    def coordinates(self) -> tuple[float, float, float]:
        '''Nodal coordinates.'''
        return self._coordinates

    # attribute slots
    __slots__ = ('_coordinates',)

    def __init__(self, coordinates: tuple[float, float, float]) -> None:
        '''Node constructor.'''
        if len(coordinates) != 3: raise ValueError(f'node requires 3 coordinates (got {len(coordinates)})')
        self._coordinates: tuple[float, float, float] = coordinates
