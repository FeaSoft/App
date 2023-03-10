from vtkmodules.vtkCommonDataModel import VTK_TRIANGLE, VTK_QUAD, VTK_TETRA, VTK_PYRAMID, VTK_WEDGE, VTK_HEXAHEDRON
from dataModel.modelingSpaces import ModelingSpaces
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
    def modelingSpace(self) -> ModelingSpaces:
        '''Number of element nodes.'''
        match self._elementType:
            case ElementTypes.E2D3: return ModelingSpaces.TwoDimensional
            case ElementTypes.E2D4: return ModelingSpaces.TwoDimensional
            case ElementTypes.E3D4: return ModelingSpaces.ThreeDimensional
            case ElementTypes.E3D5: return ModelingSpaces.ThreeDimensional
            case ElementTypes.E3D6: return ModelingSpaces.ThreeDimensional
            case ElementTypes.E3D8: return ModelingSpaces.ThreeDimensional

    @property
    def surfaces(self) -> tuple[tuple[int, ...], ...]:
        '''Gets the surfaces (nodal connectivity).'''
        match self._elementType:
            case ElementTypes.E2D3: return (
                (0, 1),
                (1, 2),
                (2, 0),
            )
            case ElementTypes.E2D4: return (
                (0, 1),
                (1, 2),
                (2, 3),
                (3, 0),
            )
            case ElementTypes.E3D4: return (
                (0, 2, 1),
                (0, 3, 2),
                (0, 1, 3),
                (1, 2, 3),
            )
            case ElementTypes.E3D5: return (
                (0, 3, 2, 1),
                (0, 1, 4),
                (1, 2, 4),
                (2, 3, 4),
                (3, 0, 4),
            )
            case ElementTypes.E3D6: return (
                (0, 2, 1),
                (3, 4, 5),
                (0, 3, 5, 2),
                (0, 1, 4, 3),
                (2, 5, 4, 1),
            )
            case ElementTypes.E3D8: return (
                (0, 3, 2, 1),
                (4, 5, 6, 7),
                (0, 1, 5, 4),
                (1, 2, 6, 5),
                (2, 3, 7, 6),
                (3, 0, 4, 7),
            )

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
