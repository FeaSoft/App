from typing import cast
from dataModel.stressStates import StressStates
from dataModel.modelingSpaces import ModelingSpaces
from dataModel.mesh import Mesh
from dataModel.dataObject import DataObject
from dataModel.indexSet import NodeSet, ElementSet
from dataModel.material import Material
from dataModel.section import Section
from dataModel.concentratedLoad import ConcentratedLoad
from dataModel.boundaryCondition import BoundaryCondition
from dataModel.dataObjectContainer import DataObjectContainer

class ModelDatabase:
    '''
    Definition of a finite element model database.
    '''

    @property
    def name(self) -> str:
        '''Model database name.'''
        return f'Model Database (Solid-{self._mesh.modelingSpace.value}D)'

    @property
    def stressStates(self) -> tuple[str, ...]:
        '''Available stress states.'''
        match self._mesh.modelingSpace:
            case ModelingSpaces.TwoDimensional: return (StressStates.CPS.name, StressStates.CPE.name)
            case ModelingSpaces.ThreeDimensional: return (StressStates.C3D.name,)

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
    def boundaryConditions(self) -> DataObjectContainer:
        '''Model database boundary conditions.'''
        return self._boundaryConditions

    # attribute slots
    __slots__ = (
        '_mesh', '_nodeSets', '_elementSets', '_materials', '_sections', '_concentratedLoads', '_boundaryConditions'
    )

    def __init__(self, mesh: Mesh) -> None:
        '''Model database constructor.'''
        self._mesh: Mesh = mesh
        self._nodeSets: DataObjectContainer = DataObjectContainer(
            NodeSet, 'Node Sets', 'Node-Set-', self.isAssigned
        )
        self._elementSets: DataObjectContainer = DataObjectContainer(
            ElementSet, 'Element Sets', 'Element-Set-', self.isAssigned
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
            case Material():
                for section in self._sections.dataObjects():
                    if cast(Section, section).materialName == dataObject.name:
                        return True
            case Section() | ConcentratedLoad() | BoundaryCondition():
                pass
            case _:
                pass
        return False
