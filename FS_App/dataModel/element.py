from vtkmodules.vtkCommonDataModel import VTK_TRIANGLE, VTK_QUAD, VTK_TETRA, VTK_PYRAMID, VTK_WEDGE, VTK_HEXAHEDRON
from dataModel.elementTypes import ElementTypes

class Element:
    '''
    Definition of a finite element.
    '''

    @property
    def elementType(self) -> ElementTypes:
        '''Finite element type.'''
        return self._elementType

    @property
    def cellType(self) -> int:
        '''Corresponding VTK cell type.'''
        match self._elementType:
            case ElementTypes.E2D3: return VTK_TRIANGLE
            case ElementTypes.E2D4: return VTK_QUAD
            case ElementTypes.E3D4: return VTK_TETRA
            case ElementTypes.E3D5: return VTK_PYRAMID
            case ElementTypes.E3D6: return VTK_WEDGE
            case ElementTypes.E3D8: return VTK_HEXAHEDRON

    @property
    def nodeCount(self) -> int:
        '''Number of element nodes.'''
        match self._elementType:
            case ElementTypes.E2D3: return 3
            case ElementTypes.E2D4: return 4
            case ElementTypes.E3D4: return 4
            case ElementTypes.E3D5: return 5
            case ElementTypes.E3D6: return 6
            case ElementTypes.E3D8: return 8

    @property
    def nodeIndices(self) -> tuple[int, ...]:
        '''Nodal connectivity.'''
        return self._nodeIndices

    # attribute slots
    __slots__ = ('_elementType', '_nodeIndices')

    def __init__(self, elementType: ElementTypes | str, nodeIndices: tuple[int, ...]) -> None:
        '''Element constructor.'''
        if isinstance(elementType, ElementTypes): self._elementType: ElementTypes = elementType
        else: self._elementType: ElementTypes = ElementTypes[elementType]
        self._nodeIndices: tuple[int, ...] = nodeIndices
        if len(nodeIndices) != self.nodeCount:
            raise ValueError(
                f'element {self._elementType.name} requires {self.nodeCount} nodes (got {len(nodeIndices)})'
            )
