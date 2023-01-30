from collections.abc import Sequence
from visualization.rendering.renderObject import RenderObject
from vtkmodules.vtkCommonDataModel import vtkPolyData, vtkUnstructuredGrid
from vtkmodules.vtkFiltersCore import vtkGlyph3D
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkRenderingCore import vtkPolyDataMapper, vtkActor

class PointsRenderObject(RenderObject):
    '''
    Renderable points (as spheres).
    '''

    # attribute slots
    __slots__ = ('_centers', '_source', '_polyData', '_glyph', '_mapper', '_actor')

    def __init__(self, dataSet: vtkUnstructuredGrid, indices: Sequence[int]) -> None:
        '''Points render object constructor.'''
        # center of spheres
        self._centers: vtkPoints = vtkPoints()
        self._centers.SetNumberOfPoints(len(indices))
        for i, index in enumerate(indices):
            self._centers.SetPoint(i, dataSet.GetPoint(index))
        # sphere source
        self._source: vtkSphereSource = vtkSphereSource()
        self._source.SetPhiResolution(8)
        self._source.SetThetaResolution(8)
        self._source.Update() # type: ignore
        # poly data
        self._polyData: vtkPolyData = vtkPolyData()
        self._polyData.SetPoints(self._centers) # type: ignore
        # glyph
        self._glyph: vtkGlyph3D = vtkGlyph3D()
        self._glyph.SetInputData(0, self._polyData) # type: ignore
        self._glyph.SetInputConnection(1, self._source.GetOutputPort())
        self._glyph.Update() # type: ignore
        # mapper
        self._mapper: vtkPolyDataMapper = vtkPolyDataMapper()
        self._mapper.SetInputConnection(self._glyph.GetOutputPort())
        self._mapper.Update() # type: ignore
        # actor
        self._actor: vtkActor = vtkActor()
        self._actor.SetMapper(self._mapper)
        self._actor.GetProperty().LightingOff()

    def actors(self) -> tuple[vtkActor, ...]:
        '''The renderable VTK actors.'''
        return (self._actor,)

    def setColor(self, color: tuple[float, float, float]) -> None:
        '''Sets the renderable object color.'''
        self._actor.GetProperty().SetColor(*color)
