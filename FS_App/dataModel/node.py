class Node:
    '''
    Definition of a finite element node.
    '''

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
