from collections.abc import Callable, Iterable
from dataModel.dataObject import DataObject

class SurfaceSet(DataObject):
    '''
    Definition of a surface set.
    '''

    @property
    def count(self) -> int:
        '''Number of surfaces in the set.'''
        return len(self._surfaces)

    # attribute slots
    __slots__ = ('_surfaces',)

    def __init__(
        self,
        indexGetter: Callable[[DataObject], int],
        nameGetter: Callable[[DataObject], str],
        nameSetter: Callable[[DataObject, str], None],
        isAssignedGetter: Callable[[DataObject], bool]
    ) -> None:
        '''Surface set constructor.'''
        super().__init__(indexGetter, nameGetter, nameSetter, isAssignedGetter)
        self._surfaces: set[tuple[int, tuple[int, ...]]] = set()

    def add(self, surfaces: Iterable[tuple[int, tuple[int, ...]]]) -> None:
        '''Adds the specified surfaces to the set.'''
        self._surfaces.update(surfaces)
        self.notifyPropertyChanged('count')

    def remove(self, surfaces: Iterable[tuple[int, tuple[int, ...]]]) -> None:
        '''Removes the specified surfaces from the set.'''
        self._surfaces.difference_update(surfaces)
        self.notifyPropertyChanged('count')

    def surfaces(self) -> tuple[tuple[int, tuple[int, ...]], ...]:
        '''Returns the surfaces of the set.'''
        return tuple(self._surfaces)

    def flipNormals(self) -> None:
        '''Flips the surface normals by reversing the nodal surface connectivity.'''
        self._surfaces = set(
            (elementIndex, tuple(reversed(connectivity))) for elementIndex, connectivity in self._surfaces
        )
