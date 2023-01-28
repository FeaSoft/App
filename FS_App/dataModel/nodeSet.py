from collections.abc import Callable, Iterable
from dataModel.dataObject import DataObject

class NodeSet(DataObject):
    '''
    Definition of a node index set.
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
        '''Node set constructor.'''
        super().__init__(nameGetter, nameSetter)
        self._indices: set[int] = set()

    def add(self, indices: int | Iterable[int]) -> None:
        '''Adds the specified indices (or index) to the set.'''
        if isinstance(indices, int): self._indices.add(indices)
        else: self._indices.update(indices)
