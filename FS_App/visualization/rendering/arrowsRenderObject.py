from typing import Literal
from collections.abc import Sequence
from visualization.rendering.renderObject import RenderObject
from vtkmodules.vtkCommonCore import vtkPoints, vtkFloatArray
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersCore import vtkGlyph3D
from vtkmodules.vtkFiltersSources import vtkArrowSource
from vtkmodules.vtkRenderingCore import vtkPolyDataMapper, vtkActor

class ArrowsRenderObject(RenderObject):
    '''
    Renderable arrows.
    '''

    # attribute slots
    __slots__ = ('_origins', '_directions', '_source', '_polyData', '_glyph', '_mapper', '_actor')

    def __init__(
        self,
        origins: Sequence[tuple[float, float, float]],
        directions: Sequence[tuple[float, float, float]],
        arrowType: Literal['Normal', 'Flipped', 'NoShaft'],
        color: tuple[float, float, float] | None = None
    ) -> None:
        '''Arrows render object constructor.'''
        super().__init__()
        # origins
        self._origins: vtkPoints = vtkPoints()
        self._origins.SetNumberOfPoints(len(origins))
        for i, origin in enumerate(origins):
            self._origins.SetPoint(i, origin)
        # directions
        self._directions: vtkFloatArray = vtkFloatArray()
        self._directions.SetName('directions')
        self._directions.SetNumberOfComponents(3)
        self._directions.SetNumberOfTuples(len(directions))
        for i, direction in enumerate(directions):
            if arrowType == 'NoShaft': direction = tuple(-x for x in direction)
            self._directions.SetTuple3(i, *direction)
        # source
        self._source: vtkArrowSource = vtkArrowSource()
        if arrowType == 'NoShaft': self._source.SetShaftRadius(0)
        if arrowType == 'NoShaft': self._source.InvertOn()
        self._source.SetTipResolution(16)
        self._source.SetShaftResolution(16)
        self._source.Update() # type: ignore
        # poly data
        self._polyData: vtkPolyData = vtkPolyData()
        self._polyData.SetPoints(self._origins)                  # type: ignore
        self._polyData.GetPointData().AddArray(self._directions) # type: ignore
        self._polyData.GetPointData().SetActiveNormals(self._directions.GetName())
        # glyph
        self._glyph: vtkGlyph3D = vtkGlyph3D()
        self._glyph.SetObjectName('arrows')
        self._glyph.SetInputData(0, self._polyData) # type: ignore
        self._glyph.SetInputConnection(1, self._source.GetOutputPort())
        self._glyph.SetVectorModeToUseNormal()
        self._glyph.Update() # type: ignore
        # mapper
        self._mapper: vtkPolyDataMapper = vtkPolyDataMapper()
        self._mapper.SetInputConnection(self._glyph.GetOutputPort())
        self._mapper.Update() # type: ignore
        # actor
        self._actor: vtkActor = vtkActor()
        self._actor.SetMapper(self._mapper)
        self._actor.GetProperty().LightingOff()
        if color: self._actor.GetProperty().SetColor(*color)

    def actors(self) -> Sequence[vtkActor]:
        '''The renderable VTK actors.'''
        return (self._actor,)
