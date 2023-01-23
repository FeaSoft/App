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
        return 'Model Database (Solid-3D)'

    @property
    def stressStates(self) -> tuple[str, ...]:
        '''Available stress states.'''
        return ('2D Plane Stress', '2D Plane Strain', '3D General')

    @property
    def materials(self) -> DataObjectContainer:
        '''Model database materials.'''
        return self._materials

    @property
    def sections(self) -> DataObjectContainer:
        '''Model database sections.'''
        return self._sections

    # attribute slots
    __slots__ = ('_materials', '_sections')

    def __init__(self) -> None:
        '''Model database constructor.'''
        self._materials: DataObjectContainer = DataObjectContainer(Material, 'Materials', 'Material-')
        self._sections: DataObjectContainer = DataObjectContainer(Section, 'Sections', 'Section-')
