import math
import visualization.utility as vu
from abc import ABC, abstractmethod
from typing import Literal, Any, cast
from collections.abc import Sequence, Callable
from visualization.rendering import PointsRenderObject, CellsRenderObject
from vtkmodules.vtkCommonExecutionModel import vtkAlgorithmOutput, vtkAlgorithm
from vtkmodules.vtkCommonCore import vtkObject, vtkCommand, vtkPoints
from vtkmodules.vtkCommonDataModel import vtkCellArray, vtkPolyData, vtkUnstructuredGrid
from vtkmodules.vtkFiltersCore import vtkGlyph3D
from vtkmodules.vtkFiltersSources import vtkLineSource
from vtkmodules.vtkFiltersExtraction import vtkExtractGeometry
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleTrackballCamera
from vtkmodules.vtkRenderingCore import (
    vtkRenderWindow, vtkRenderer, vtkRenderWindowInteractor, vtkActor2D, vtkActor, vtkPolyDataMapper2D, vtkCoordinate,
    vtkMapper, vtkPointPicker, vtkCellPicker, vtkPicker, vtkAreaPicker
)

class InteractionStyle(ABC):
    '''
    Abstract base class for interaction styles.
    '''

    @staticmethod
    def recomputeGlyphSize(renderer: vtkRenderer, render: bool = True) -> None:
        '''Recomputes the glyph size so it is independent of camera zoom.'''
        for i in range(renderer.GetActors().GetNumberOfItems()):
            actor: vtkActor = cast(vtkActor, renderer.GetActors().GetItemAsObject(i))
            mapper: vtkMapper = actor.GetMapper()
            output: vtkAlgorithmOutput | None = mapper.GetInputConnection(0, 0)
            producer: vtkAlgorithm | None = output.GetProducer() if output else None
            if isinstance(producer, vtkGlyph3D):
                actorPosition: tuple[float, float, float] = actor.GetPosition()
                cameraPosition: tuple[float, float, float] = renderer.GetActiveCamera().GetPosition()
                dx: float = cameraPosition[0] - actorPosition[0]
                dy: float = cameraPosition[1] - actorPosition[1]
                dz: float = cameraPosition[2] - actorPosition[2]
                distance: float = math.sqrt(dx*dx + dy*dy + dz*dz)
                scale: float = distance*0.005
                producer.SetScaleFactor(scale)
                producer.Modified()
        if render: renderer.GetRenderWindow().Render()

    @staticmethod
    def newLineHint(pointA: tuple[int, int], pointB: tuple[int, int]) -> vtkActor2D:
        '''Creates a new 2D line hint.'''
        # source
        lineSource: vtkLineSource = vtkLineSource()
        lineSource.SetPoint1(*pointA, 0.0)
        lineSource.SetPoint2(*pointB, 0.0)
        lineSource.Update() # type: ignore
        # mapper
        polyDataMapper2D: vtkPolyDataMapper2D = vtkPolyDataMapper2D()
        polyDataMapper2D.SetInputConnection(lineSource.GetOutputPort())
        polyDataMapper2D.Update() # type: ignore
        # actor
        actor2D: vtkActor2D = vtkActor2D()
        actor2D.SetMapper(polyDataMapper2D)
        return actor2D

    @staticmethod
    def newArcHint(pointA: tuple[int, int], pointB: tuple[int, int], renderWindowSize: tuple[int, int]) -> vtkActor2D:
        '''Creates a new 2D arc hint.'''
        # compute start and segment angles
        angleA: float = math.atan2(pointA[1] - renderWindowSize[1]/2.0, pointA[0] - renderWindowSize[0]/2.0)
        angleB: float = math.atan2(pointB[1] - renderWindowSize[1]/2.0, pointB[0] - renderWindowSize[0]/2.0)
        if angleA < 0.0: angleA += 2.0*math.pi
        if angleB < 0.0: angleB += 2.0*math.pi
        startAngle: float = angleA if angleA < angleB else angleB
        segmentAngle: float = angleB - angleA if angleB > angleA else angleA - angleB
        if segmentAngle > math.pi:
            segmentAngle = 2.0*math.pi - segmentAngle
            startAngle = angleB if startAngle == angleA else angleA
        # resolution
        numberOfSegments: int = 64
        numberOfPoints: int = numberOfSegments + 1
        # stretch/shrink factors
        factorX: float = renderWindowSize[1]/renderWindowSize[0] if renderWindowSize[0] > renderWindowSize[1] else 1.0
        factorY: float = renderWindowSize[0]/renderWindowSize[1] if renderWindowSize[1] > renderWindowSize[0] else 1.0
        # points
        points: vtkPoints = vtkPoints()
        points.SetNumberOfPoints(numberOfPoints)
        for i in range(numberOfPoints):
            r: float = 0.45
            theta: float = startAngle + i*segmentAngle/numberOfSegments
            x: float = r*math.cos(theta)*factorX
            y: float = r*math.sin(theta)*factorY
            points.SetPoint(i, x, y, 0.0)
        # lines
        lines: vtkCellArray = vtkCellArray()
        lines.InsertNextCell(numberOfPoints, range(numberOfPoints)) # type: ignore
        # data set
        polyData: vtkPolyData = vtkPolyData()
        polyData.SetPoints(points) # type: ignore
        polyData.SetLines(lines)
        # transform coordinate
        coordinate: vtkCoordinate = vtkCoordinate()
        coordinate.SetCoordinateSystemToNormalizedViewport()
        # mapper
        polyDataMapper2D: vtkPolyDataMapper2D = vtkPolyDataMapper2D()
        polyDataMapper2D.SetTransformCoordinate(coordinate)
        polyDataMapper2D.SetInputData(polyData) # type: ignore
        polyDataMapper2D.Update()               # type: ignore
        # actor
        actor2D: vtkActor2D = vtkActor2D()
        actor2D.SetMapper(polyDataMapper2D)
        actor2D.GetPositionCoordinate().SetCoordinateSystemToNormalizedViewport()
        actor2D.SetPosition(0.5, 0.5)
        return actor2D

    @staticmethod
    def newRectangleHint(pointA: tuple[int, int], pointB: tuple[int, int]) -> vtkActor2D:
        '''Creates a new 2D rectangle hint.'''
        # points
        points: vtkPoints = vtkPoints()
        points.SetNumberOfPoints(4)
        points.SetPoint(0, pointA[0], pointA[1], 0.0)
        points.SetPoint(1, pointB[0], pointA[1], 0.0)
        points.SetPoint(2, pointB[0], pointB[1], 0.0)
        points.SetPoint(3, pointA[0], pointB[1], 0.0)
        # lines
        lines: vtkCellArray = vtkCellArray()
        lines.InsertNextCell(5, (0, 1, 2, 3, 0)) # type: ignore
        # data set
        polyData: vtkPolyData = vtkPolyData()
        polyData.SetPoints(points)  # type: ignore
        polyData.SetLines(lines)
        # mapper
        polyDataMapper2D: vtkPolyDataMapper2D = vtkPolyDataMapper2D()
        polyDataMapper2D.SetInputData(polyData) # type: ignore
        polyDataMapper2D.Update()               # type: ignore
        # actor
        actor2D: vtkActor2D = vtkActor2D()
        actor2D.SetMapper(polyDataMapper2D)
        return actor2D

    @staticmethod
    def newPointsHint(unstructuredGrid: vtkUnstructuredGrid, indices: Sequence[int]) -> vtkActor:
        '''Creates a new 3D points hint.'''
        renderObject: PointsRenderObject = PointsRenderObject(unstructuredGrid, indices)
        renderObject.setColor((1.0, 0.5, 0.0))
        return renderObject.actors()[0]

    @staticmethod
    def newCellsHint(unstructuredGrid: vtkUnstructuredGrid, indices: Sequence[int]) -> vtkActor:
        '''Creates a new 3D cells hint.'''
        renderObject: CellsRenderObject = CellsRenderObject(unstructuredGrid, indices)
        renderObject.setColor((1.0, 0.5, 0.0))
        return renderObject.actors()[0]

    @staticmethod
    def pickSingle(
        point: tuple[int, int],
        target: Literal['Points', 'Cells'],
        renderer: vtkRenderer
    ) -> tuple[int, vtkActor | None]:
        '''Picks a single point or cell.'''
        # perform pick operation
        picker: vtkPicker = vtkPointPicker() if target == 'Points' else vtkCellPicker()
        picker.SetTolerance(0.003 if target == 'Points' else 0.0)
        picker.Pick(*point, 0.0, renderer)
        # get picked data set (if any)
        actor: vtkActor | None = picker.GetActor()
        mapper: vtkMapper | None = actor.GetMapper() if actor else None
        dataSet: Any | None = mapper.GetInput() if mapper else None # type: ignore
        # return
        if isinstance(dataSet, vtkUnstructuredGrid):
            if target == 'Points':
                index: int = picker.GetPointId()
                return index, InteractionStyle.newPointsHint(dataSet, (index,))
            else:
                index: int = picker.GetCellId()                                # type: ignore
                return index, InteractionStyle.newCellsHint(dataSet, (index,)) # type: ignore
        return -1, None

    @staticmethod
    def pickMultiple(
        pointA: tuple[int, int],
        pointB: tuple[int, int],
        target: Literal['Points', 'Cells'],
        renderer: vtkRenderer
    ) -> Sequence[int]:
        '''Picks multiple points or cells.'''
        picker: vtkAreaPicker = vtkAreaPicker()
        picker.AreaPick(*pointA, *pointB, renderer)
        for i in range(picker.GetProp3Ds().GetNumberOfItems()):
            actor: vtkActor = cast(vtkActor, picker.GetProp3Ds().GetItemAsObject(i))
            mapper: vtkMapper = actor.GetMapper()
            dataSet: Any | None = mapper.GetInput() # type: ignore
            if isinstance(dataSet, vtkUnstructuredGrid):
                filter: vtkExtractGeometry = vtkExtractGeometry()
                filter.SetImplicitFunction(picker.GetFrustum())     # type: ignore
                filter.SetInputData(dataSet)                        # type: ignore
                filter.Update()                                     # type: ignore
                selection: vtkUnstructuredGrid = filter.GetOutput() # type: ignore
                if target == 'Points': return vu.findPointIndices(dataSet, selection)
                else: return vu.findCellIndices(dataSet, selection)
        return ()

    @property
    def base(self) -> vtkInteractorStyleTrackballCamera:
        '''The VTK interactor style.'''
        return self._base

    @property
    def _interactor(self) -> vtkRenderWindowInteractor:
        '''The VTK interactor.'''
        return self._base.GetInteractor()

    @property
    def _renderWindow(self) -> vtkRenderWindow:
        '''The VTK render window.'''
        return self._interactor.GetRenderWindow()

    @property
    def _renderer(self) -> vtkRenderer:
        '''The VTK renderer.'''
        return self._renderWindow.GetRenderers().GetFirstRenderer()

    # attribute slots
    __slots__ = (
        '_base', '_isLeftButtonDown', '_isMiddleButtonDown', '_isRightButtonDown', '_pointA', '_pointB', '_hint2D',
        '_onPicked', '_pickTarget'
    )

    @abstractmethod
    def __init__(self) -> None:
        '''Interaction style constructor.'''
        super().__init__()
        self._base: vtkInteractorStyleTrackballCamera = vtkInteractorStyleTrackballCamera()
        self._base.AddObserver(vtkCommand.LeftButtonPressEvent, self.onLeftButtonPress)
        self._base.AddObserver(vtkCommand.LeftButtonReleaseEvent, self.onLeftButtonRelease)
        self._base.AddObserver(vtkCommand.MiddleButtonPressEvent, self.onMiddleButtonPress)
        self._base.AddObserver(vtkCommand.MiddleButtonReleaseEvent, self.onMiddleButtonRelease)
        self._base.AddObserver(vtkCommand.RightButtonPressEvent, self.onRightButtonPress)
        self._base.AddObserver(vtkCommand.RightButtonReleaseEvent, self.onRightButtonRelease)
        self._base.AddObserver(vtkCommand.MouseWheelForwardEvent, self.onMouseWheelForward)
        self._base.AddObserver(vtkCommand.MouseWheelBackwardEvent, self.onMouseWheelBackward)
        self._base.AddObserver(vtkCommand.MouseMoveEvent, self.onMouseMove)
        self._isLeftButtonDown: bool = False
        self._isMiddleButtonDown: bool = False
        self._isRightButtonDown: bool = False
        self._pointA: tuple[int, int] = (0, 0)
        self._pointB: tuple[int, int] = (0, 0)
        self._hint2D: vtkActor2D | None = None
        self._onPicked: Callable[[Sequence[int], bool], None] | None = None
        self._pickTarget: Literal['Points', 'Cells'] | None = None

    def setPickAction(
        self,
        onPicked: Callable[[Sequence[int], bool], None] | None,
        pickTarget: Literal['Points', 'Cells'] | None
    ) -> None:
        '''Sets the callback function for when picking is performed.'''
        self._onPicked = onPicked
        self._pickTarget = pickTarget

    @abstractmethod
    def onLeftButtonPress(self, sender: vtkObject, event: str) -> None:
        '''On left button press.'''
        ...

    @abstractmethod
    def onLeftButtonRelease(self, sender: vtkObject, event: str) -> None:
        '''On left button release.'''
        ...

    def onMiddleButtonPress(self, sender: vtkObject, event: str) -> None:
        '''On middle button press.'''
        if self._isLeftButtonDown or self._isRightButtonDown: return
        self._isMiddleButtonDown = True
        self._pointA = self._interactor.GetEventPosition()
        self._base.StartPan()

    def onMiddleButtonRelease(self, sender: vtkObject, event: str) -> None:
        '''On middle button release.'''
        self._isMiddleButtonDown = False
        if self._hint2D: self._renderer.RemoveActor2D(self._hint2D)
        self._base.EndPan()

    def onRightButtonPress(self, sender: vtkObject, event: str) -> None:
        '''On right button press.'''
        if self._isLeftButtonDown or self._isMiddleButtonDown: return
        self._isRightButtonDown = True
        self._pointA = self._interactor.GetEventPosition()
        self._base.StartDolly()

    def onRightButtonRelease(self, sender: vtkObject, event: str) -> None:
        '''On right button release.'''
        self._isRightButtonDown = False
        if self._hint2D: self._renderer.RemoveActor2D(self._hint2D)
        self._base.EndDolly()

    def onMouseWheelForward(self, sender: vtkObject, event: str) -> None:
        '''On mouse wheel forward.'''
        if self._isLeftButtonDown or self._isMiddleButtonDown or self._isRightButtonDown: return
        self._base.OnMouseWheelForward()
        self.recomputeGlyphSize(self._renderer)

    def onMouseWheelBackward(self, sender: vtkObject, event: str) -> None:
        '''On mouse wheel backward.'''
        if self._isLeftButtonDown or self._isMiddleButtonDown or self._isRightButtonDown: return
        self._base.OnMouseWheelBackward()
        self.recomputeGlyphSize(self._renderer)

    def onMouseMove(self, sender: vtkObject, event: str) -> None:
        '''On mouse move.'''
        if self._isRightButtonDown: self.recomputeGlyphSize(self._renderer)
        if self._isMiddleButtonDown or self._isRightButtonDown:
            if self._hint2D: self._renderer.RemoveActor2D(self._hint2D)
            self._pointB = self._interactor.GetEventPosition() if self._isMiddleButtonDown else (
                self._pointA[0], self._interactor.GetEventPosition()[1]
            )
            self._hint2D = self.newLineHint(self._pointA, self._pointB)
            self._renderer.AddActor2D(self._hint2D)
        self._base.OnMouseMove()
