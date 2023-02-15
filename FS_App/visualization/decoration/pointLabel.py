from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkPolyData
from vtkmodules.vtkFiltersCore import vtkGlyph3D
from vtkmodules.vtkFiltersSources import vtkSphereSource
from vtkmodules.vtkRenderingCore import vtkPolyDataMapper, vtkActor, vtkTextActor, vtkRenderer

class PointLabel:
    '''
    Grid point label.
    '''

    # attribute slots
    __slots__ = ('_sphereCenter', '_source', '_polyData', '_glyph', '_mapper', '_sphereActor', '_textActor')

    def __init__(self, color: tuple[float, float, float], fontSize: int) -> None:
        '''Point label constructor.'''
        # sphere center
        self._sphereCenter: vtkPoints = vtkPoints()
        self._sphereCenter.SetNumberOfPoints(1)
        self._sphereCenter.SetPoint(0, 0.0, 0.0, 0.0)
        # sphere source
        self._source: vtkSphereSource = vtkSphereSource()
        self._source.SetPhiResolution(8)
        self._source.SetThetaResolution(8)
        self._source.Update() # type: ignore
        # poly data
        self._polyData: vtkPolyData = vtkPolyData()
        self._polyData.SetPoints(self._sphereCenter) # type: ignore
        # glyph
        self._glyph: vtkGlyph3D = vtkGlyph3D()
        self._glyph.SetObjectName('points')
        self._glyph.SetInputData(0, self._polyData) # type: ignore
        self._glyph.SetInputConnection(1, self._source.GetOutputPort())
        self._glyph.Update() # type: ignore
        # mapper
        self._mapper: vtkPolyDataMapper = vtkPolyDataMapper()
        self._mapper.SetInputConnection(self._glyph.GetOutputPort())
        self._mapper.Update() # type: ignore
        # sphere actor
        self._sphereActor: vtkActor = vtkActor()
        self._sphereActor.SetMapper(self._mapper)
        self._sphereActor.GetProperty().LightingOff()
        self._sphereActor.GetProperty().SetColor(*color)
        # text actor
        self._textActor: vtkTextActor = vtkTextActor()
        self._textActor.SetTextScaleModeToNone()
        self._textActor.GetTextProperty().SetColor(color)
        self._textActor.GetTextProperty().SetFontSize(fontSize)
        self._textActor.GetTextProperty().SetFontFamilyToCourier()
        self._textActor.GetTextProperty().ItalicOff()
        self._textActor.GetTextProperty().ShadowOn()
        self._textActor.GetTextProperty().BoldOff()
        self._textActor.GetTextProperty().SetJustificationToLeft()
        self._textActor.GetTextProperty().SetVerticalJustificationToBottom()
        self._textActor.GetPositionCoordinate().SetCoordinateSystemToWorld()

    def initialize(self, renderer: vtkRenderer) -> None:
        '''Sets the renderer.'''
        renderer.AddActor(self._sphereActor)
        renderer.AddActor2D(self._textActor)

    def setText(self, text: str) -> None:
        '''Sets the text.'''
        self._textActor.SetInput(text)

    def setPosition(self, position: tuple[float, float, float]) -> None:
        '''Sets the position.'''
        self._textActor.GetPositionCoordinate().SetValue(position)
        self._sphereCenter.SetPoint(0, position)
        self._sphereCenter.Modified()

    def setColor(self, color: tuple[float, float, float]) -> None:
        '''Sets the text color.'''
        self._sphereActor.GetProperty().SetColor(*color)
        self._textActor.GetTextProperty().SetColor(color)

    def setFontSize(self, size: int) -> None:
        '''Sets the font size.'''
        self._textActor.GetTextProperty().SetFontSize(size)

    def setVisible(self, value: bool) -> None:
        '''Sets the visibility of the actor.'''
        self._sphereActor.SetVisibility(value)
        self._textActor.SetVisibility(value)
