from collections.abc import Callable, Sequence
from dataModel.dataObject import DataObject

class IndexSet(DataObject):
    '''
    Definition of an index set.
    '''

    @property
    def count(self) -> int:
        '''Number of indices in the set.'''
        return len(self._indices)

    # attribute slots
    __slots__ = ('_indices',)

    def __init__(
        self,
        nameGetter: Callable[[DataObject], str],
        nameSetter: Callable[[DataObject, str], None]
    ) -> None:
        '''Index set constructor.'''
        super().__init__(nameGetter, nameSetter)
        self._indices: set[int] = set()

    def add(self, indices: Sequence[int]) -> None:
        '''Adds the specified indices to the set.'''
        self._indices.update(indices)
        self.notifyPropertyChanged('count')

    def remove(self, indices: Sequence[int]) -> None:
        '''Removes the specified indices from the set.'''
        self._indices.difference_update(indices)
        self.notifyPropertyChanged('count')

    def indices(self) -> tuple[int, ...]:
        '''Returns the indices of the set.'''
        return tuple(self._indices)

class NodeSet(IndexSet):
    '''
    Definition of a node index set.
    '''

class ElementSet(IndexSet):
    '''
    Definition of an element index set.
    '''
