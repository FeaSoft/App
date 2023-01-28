import visualization.preferences as vp
from dataModel import Mesh
from visualization.rendering.renderObject import RenderObject
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid
from vtkmodules.vtkRenderingCore import vtkDataSetMapper, vtkActor

class MeshRenderObject(RenderObject):
    '''
    Finite element mesh renderable object.
    '''

    @staticmethod
    def buildDataSet(mesh: Mesh) -> vtkUnstructuredGrid:
        '''Builds the vtkUnstructuredGrid data set object.'''
        # instantiate the data set object
        dataSet: vtkUnstructuredGrid = vtkUnstructuredGrid()
        # set point coordinates
        points: vtkPoints = vtkPoints()
        points.SetNumberOfPoints(len(mesh.nodes))
        for i, node in enumerate(mesh.nodes):
            points.SetPoint(i, node.coordinates)
        dataSet.SetPoints(points) # type: ignore
        # set cell connectivity
        dataSet.AllocateEstimate(len(mesh.elements), 8)
        for element in mesh.elements:
            dataSet.InsertNextCell(element.cellType, element.nodeCount, element.nodeIndices) # type: ignore
        dataSet.Squeeze()
        # done
        return dataSet

    @property
    def actors(self) -> tuple[vtkActor, ...]:
        '''The renderable VTK actors.'''
        return (self._actor,)

    # attribute slots
    __slots__ = ('_dataSet', '_dataSetMapper', '_actor')

    def __init__(self, mesh: Mesh) -> None:
        '''Mesh render object constructor.'''
        super().__init__()
        # data set
        self._dataSet: vtkUnstructuredGrid = self.buildDataSet(mesh)
        # data set mapper
        self._dataSetMapper: vtkDataSetMapper = vtkDataSetMapper()
        self._dataSetMapper.SetInputData(self._dataSet) # type: ignore
        self._dataSetMapper.Update() # type: ignore
        # actor
        self._actor: vtkActor = vtkActor()
        self._actor.SetMapper(self._dataSetMapper)
        self._actor.GetProperty().SetColor(*vp.getMeshCellColor())
        self._actor.GetProperty().SetEdgeColor(*vp.getMeshLineColor())
        self._actor.GetProperty().SetEdgeVisibility(1 if vp.getMeshLineVisibility() else 0)
