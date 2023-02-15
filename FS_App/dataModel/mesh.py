from collections.abc import Sequence
from dataModel.node import Node
from dataModel.element import Element
from dataModel.elementTypes import ElementTypes
from dataModel.modelingSpaces import ModelingSpaces

class Mesh:
    '''
    Definition of a finite element mesh.
    '''

    @property
    def modelingSpace(self) -> ModelingSpaces:
        '''Mesh modeling space.'''
        return self._modelingSpace

    @property
    def nodes(self) -> tuple[Node]:
        '''Mesh nodes.'''
        return self._nodes

    @property
    def elements(self) -> tuple[Element]:
        '''Mesh elements.'''
        return self._elements

    @property
    def elementIndicesPerNodeIndex(self) -> tuple[tuple[int, ...], ...]:
        '''Element indices per node index.'''
        return self._elementIndicesPerNodeIndex

    # attribute slots
    __slots__ = ('_modelingSpace', '_nodes', '_elements', '_elementIndicesPerNodeIndex')

    def __init__(
        self,
        modelingSpace: ModelingSpaces | int,
        nodeData: Sequence[tuple[float, float, float]],
        elementData: Sequence[tuple[str, tuple[int, ...]]]
    ) -> None:
        '''Mesh constructor.'''
        if isinstance(modelingSpace, ModelingSpaces): self._modelingSpace: ModelingSpaces = modelingSpace
        else: self._modelingSpace: ModelingSpaces = ModelingSpaces(modelingSpace)
        self._nodes: tuple[Node, ...] = tuple(Node(coordinates) for coordinates in nodeData)
        self._elements: tuple[Element, ...] = tuple(
            Element(ElementTypes[elementType], nodeIndices) for elementType, nodeIndices in elementData
        )
        # count element indices per node index
        _counts: list[list[int]] = [[] for _ in range(len(self._nodes))]
        for i, element in enumerate(self._elements):
            for nodeIndex in element.nodeIndices:
                _counts[nodeIndex].append(i)
        self._elementIndicesPerNodeIndex: tuple[tuple[int, ...], ...] = tuple(tuple(x) for x in _counts)
