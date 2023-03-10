from typing import cast
from collections.abc import Sequence
from dataModel.stressStates import StressStates
from dataModel.modelingSpaces import ModelingSpaces
from dataModel.element import Element
from dataModel.mesh import Mesh
from dataModel.dataObject import DataObject
from dataModel.indexSet import NodeSet, ElementSet
from dataModel.surfaceSet import SurfaceSet
from dataModel.material import Material
from dataModel.section import Section
from dataModel.concentratedLoad import ConcentratedLoad
from dataModel.pressure import Pressure
from dataModel.surfaceTraction import SurfaceTraction
from dataModel.bodyLoad import BodyLoad
from dataModel.boundaryCondition import BoundaryCondition
from dataModel.dataObjectContainer import DataObjectContainer

class ModelDatabase:
    '''
    Definition of a finite element model database.
    '''

    @property
    def filePath(self) -> str:
        '''Model database file path.'''
        return self._filePath

    @filePath.setter
    def filePath(self, value: str) -> None:
        '''Model database file path (setter).'''
        self._filePath = value

    @property
    def name(self) -> str:
        '''Model database name.'''
        return f'Model Database (Solid-{self._mesh.modelingSpace.value}D)'

    @property
    def stressStates(self) -> tuple[str, ...]:
        '''Available stress states.'''
        match self._mesh.modelingSpace:
            case ModelingSpaces.TwoDimensional:
                return (StressStates.CPS.name, StressStates.CPE.name, StressStates.CAX.name)
            case ModelingSpaces.ThreeDimensional:
                return (StressStates.C3D.name,)

    @property
    def mesh(self) -> Mesh:
        '''Model database finite element mesh.'''
        return self._mesh

    @property
    def nodeSets(self) -> DataObjectContainer:
        '''Model database node sets.'''
        return self._nodeSets

    @property
    def elementSets(self) -> DataObjectContainer:
        '''Model database element sets.'''
        return self._elementSets

    @property
    def surfaceSets(self) -> DataObjectContainer:
        '''Model database surface sets.'''
        return self._surfaceSets

    @property
    def materials(self) -> DataObjectContainer:
        '''Model database materials.'''
        return self._materials

    @property
    def sections(self) -> DataObjectContainer:
        '''Model database sections.'''
        return self._sections

    @property
    def concentratedLoads(self) -> DataObjectContainer:
        '''Model database concentrated loads.'''
        return self._concentratedLoads

    @property
    def pressures(self) -> DataObjectContainer:
        '''Model database body loads.'''
        return self._pressures

    @property
    def surfaceTractions(self) -> DataObjectContainer:
        '''Model database body loads.'''
        return self._surfaceTractions

    @property
    def bodyLoads(self) -> DataObjectContainer:
        '''Model database body loads.'''
        return self._bodyLoads

    @property
    def boundaryConditions(self) -> DataObjectContainer:
        '''Model database boundary conditions.'''
        return self._boundaryConditions

    # attribute slots
    __slots__ = (
        '_filePath', '_mesh', '_nodeSets', '_elementSets', '_surfaceSets', '_materials', '_sections',
        '_concentratedLoads', '_pressures', '_surfaceTractions', '_bodyLoads', '_boundaryConditions'
    )

    def __init__(self, mesh: Mesh) -> None:
        '''Model database constructor.'''
        self._filePath: str = ''
        self._mesh: Mesh = mesh
        self._nodeSets: DataObjectContainer = DataObjectContainer(
            NodeSet, 'Node Sets', 'Node-Set-', self.isAssigned
        )
        self._elementSets: DataObjectContainer = DataObjectContainer(
            ElementSet, 'Element Sets', 'Element-Set-', self.isAssigned
        )
        self._surfaceSets: DataObjectContainer = DataObjectContainer(
            SurfaceSet, 'Surface Sets', 'Surface-Set-', self.isAssigned
        )
        self._materials: DataObjectContainer = DataObjectContainer(
            Material, 'Materials', 'Material-', self.isAssigned
        )
        self._sections: DataObjectContainer = DataObjectContainer(
            Section, 'Sections', 'Section-', self.isAssigned
        )
        self._concentratedLoads: DataObjectContainer = DataObjectContainer(
            ConcentratedLoad, 'Concentrated Loads', 'Concentrated-Load-', self.isAssigned
        )
        self._pressures: DataObjectContainer = DataObjectContainer(
            Pressure, 'Pressures', 'Pressure-', self.isAssigned
        )
        self._surfaceTractions: DataObjectContainer = DataObjectContainer(
            SurfaceTraction, 'Surface Tractions', 'Surface-Traction-', self.isAssigned
        )
        self._bodyLoads: DataObjectContainer = DataObjectContainer(
            BodyLoad, 'Body Loads', 'Body-Load-', self.isAssigned
        )
        self._boundaryConditions: DataObjectContainer = DataObjectContainer(
            BoundaryCondition, 'Boundary Conditions', 'Boundary-Condition-', self.isAssigned
        )

    def isAssigned(self, dataObject: DataObject) -> bool:
        '''Determines if the specified data object is currently assigned.'''
        match dataObject:
            case NodeSet():
                for concentratedLoad in self._concentratedLoads.dataObjects():
                    if cast(ConcentratedLoad, concentratedLoad).nodeSetName == dataObject.name:
                        return True
                for boundaryCondition in self._boundaryConditions.dataObjects():
                    if cast(BoundaryCondition, boundaryCondition).nodeSetName == dataObject.name:
                        return True
            case ElementSet():
                for section in self._sections.dataObjects():
                    if cast(Section, section).elementSetName == dataObject.name:
                        return True
                for bodyLoad in self._bodyLoads.dataObjects():
                    if cast(BodyLoad, bodyLoad).elementSetName == dataObject.name:
                        return True
            case SurfaceSet():
                for pressure in self._pressures.dataObjects():
                    if cast(Pressure, pressure).surfaceSetName == dataObject.name:
                        return True
                for surfaceTraction in self._surfaceTractions.dataObjects():
                    if cast(SurfaceTraction, surfaceTraction).surfaceSetName == dataObject.name:
                        return True
            case Material():
                for section in self._sections.dataObjects():
                    if cast(Section, section).materialName == dataObject.name:
                        return True
            case Section() | ConcentratedLoad() | Pressure() | SurfaceTraction() | BodyLoad() | BoundaryCondition():
                pass
            case _:
                pass
        return False

    def convertNodeIndicesToSurfaces(self, nodeIndices: Sequence[int]) -> set[tuple[int, tuple[int, ...]]]:
        '''Node set to surface set conversion.'''
        # get element indices
        elementIndices: set[int] = set()
        for nodeIndex in nodeIndices:
            elementIndices.update(self.mesh.elementIndicesPerNodeIndex[nodeIndex])
        # create surface set
        surfaces: set[tuple[int, tuple[int, ...]]] = set()
        for elementIndex in elementIndices:
            element: Element = self.mesh.elements[elementIndex]
            for localConnectivity in element.surfaces:
                globalConnectivity: tuple[int, ...] = tuple(element.nodeIndices[i] for i in localConnectivity)
                if all(index in nodeIndices for index in globalConnectivity):
                    surfaces.add((elementIndex, localConnectivity))
        return surfaces
