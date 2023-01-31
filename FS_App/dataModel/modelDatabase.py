from dataModel.mesh import Mesh
from dataModel.indexSet import NodeSet, ElementSet
from dataModel.material import Material
from dataModel.section import Section
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
        return ('2D Plane Stress', '2D Plane Strain', '3D General')

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

    # attribute slots
    __slots__ = ('_mesh', '_nodeSets', '_elementSets', '_materials', '_sections')

    def __init__(self, mesh: Mesh) -> None:
        '''Model database constructor.'''
        self._mesh: Mesh = mesh
        self._nodeSets: DataObjectContainer = DataObjectContainer(NodeSet, 'Node Sets', 'Node-Set-')
        self._elementSets: DataObjectContainer = DataObjectContainer(ElementSet, 'Element Sets', 'Element-Set-')
        self._materials: DataObjectContainer = DataObjectContainer(Material, 'Materials', 'Material-')
        self._sections: DataObjectContainer = DataObjectContainer(Section, 'Sections', 'Section-')
