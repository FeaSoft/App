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

    # attribute slots
    __slots__ = ('_modelingSpace', '_nodes', '_elements')

    def __init__(
        self,
        modelingSpace: ModelingSpaces,
        nodeData: Sequence[tuple[float, float, float]],
        elementData: Sequence[tuple[str, tuple[int, ...]]]
    ) -> None:
        '''Mesh constructor.'''
        self._modelingSpace: ModelingSpaces = modelingSpace
        self._nodes: tuple[Node, ...] = tuple(Node(coordinates) for coordinates in nodeData)
        self._elements: tuple[Element, ...] = tuple(
            Element(ElementTypes[elementType], nodeIndices) for elementType, nodeIndices in elementData
        )