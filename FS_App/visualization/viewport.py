import vtkmodules.vtkRenderingContextOpenGL2 # type: ignore (initialize VTK)
from typing import Literal, Any, cast
from collections.abc import Callable, Sequence
from dataModel import Mesh, NodeSet, ElementSet, ConcentratedLoad, BoundaryCondition, ModelDatabase
from visualization.decoration import Triad, Info
from visualization.rendering import (
    RenderObject, MeshRenderObject, PointsRenderObject, CellsRenderObject, ArrowsRenderObject, GroupRenderObject
)
from visualization.interaction import (
    Views, InteractionStyles, InteractionStyle, RotateInteractionStyle, PanInteractionStyle, ZoomInteractionStyle,
    PickSingleInteractionStyle, PickMultipleInteractionStyle, ProbeInteractionStyle, RulerInteractionStyle
)
from PySide6.QtWidgets import QWidget
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor # type: ignore
from vtkmodules.vtkRenderingCore import vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor

class Viewport(QVTKRenderWindowInteractor):
    '''
    Visualization viewport based on VTK.
    '''

    # class variables
    _callbacks: dict[int, Callable[[str, Any], None]] = {}
    _viewports: list['Viewport'] = []
    _interactionStyles: dict[InteractionStyles, InteractionStyle] = {
        InteractionStyles.Rotate       : RotateInteractionStyle(),
        InteractionStyles.Pan          : PanInteractionStyle(),
        InteractionStyles.Zoom         : ZoomInteractionStyle(),
        InteractionStyles.PickSingle   : PickSingleInteractionStyle(),
        InteractionStyles.PickMultiple : PickMultipleInteractionStyle(),
        InteractionStyles.Probe        : ProbeInteractionStyle(),
        InteractionStyles.Ruler        : RulerInteractionStyle()
    }
    _currentInteractionStyle: InteractionStyles = InteractionStyles.Rotate

    @classmethod
    def registerCallback(cls, callback: Callable[[str, Any], None]) -> int:
        '''
        Adds the specified callback function to the internal container of callbacks.
        Returns a key used to deregister the callback.
        '''
        key: int = 0
        while key in cls._callbacks: key += 1
        cls._callbacks[key] = callback
        return key

    @classmethod
    def deregisterCallback(cls, key: int) -> None:
        '''Removes the callback function from the internal container of callbacks using its key.'''
        del cls._callbacks[key]

    @classmethod
    def notifyOptionChanged(cls, optionName: str, optionValue: Any) -> None:
        '''This method is called when a viewport option has changed its value.'''
        for callback in cls._callbacks.values(): callback(optionName, optionValue)

    @classmethod
    def setInteractionStyle(cls, interactionStyle: InteractionStyles) -> None:
        '''Sets the viewport interaction style for all viewports.'''
        cls._currentInteractionStyle = interactionStyle
        for viewport in cls._viewports:
            viewport._interactor.SetInteractorStyle(cls._interactionStyles[cls._currentInteractionStyle].base)
            viewport._interactor.RemoveObservers('CharEvent')
        cls.notifyOptionChanged(InteractionStyles.__name__, interactionStyle)

    @property
    def info(self) -> Info:
        '''The viewport information object.'''
        return self._info

    # attribute slots
    __slots__ = (
        '_renderer', '_renderWindow', '_interactor', '_triad', '_info', '_meshRenderObject', '_selectionRenderObject'
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        '''Viewport constructor.'''
        super().__init__(parent) # type: ignore
        # register viewport
        self._viewports.append(self)
        # renderer
        self._renderer: vtkRenderer = vtkRenderer()
        self._renderer.GradientBackgroundOn()
        self._renderer.SetBackground(0.6, 0.7, 0.8)
        self._renderer.SetBackground2(0.1, 0.2, 0.3)
        # render window
        self._renderWindow: vtkRenderWindow = cast(vtkRenderWindow, self.GetRenderWindow())
        self._renderWindow.AddRenderer(self._renderer)
        # interactor
        self._interactor: vtkRenderWindowInteractor = self._renderWindow.GetInteractor()
        # triad & info
        self._triad: Triad = Triad()
        self._info: Info = Info()
        # render objects
        self._meshRenderObject: MeshRenderObject | None = None
        self._selectionRenderObject: RenderObject | None = None

    def initialize(self) -> None:
        '''Initializes the viewport.'''
        self._interactor.Initialize()
        self._triad.initialize(self._interactor)
        self._info.initialize(self._renderer)
        self.setInteractionStyle(self._currentInteractionStyle)

    def render(self) -> None:
        '''Renders the current scene.'''
        self._renderWindow.Render()

    def add(self, renderObject: RenderObject, render: bool = True) -> None:
        '''Adds the renderable visualization object to the scene.'''
        for actor in renderObject.actors(): self._renderer.AddActor(actor)
        if isinstance(renderObject, PointsRenderObject):
            InteractionStyle.recomputeGlyphSize(self._renderer, render=False)
        if render: self.render()

    def remove(self, renderObject: RenderObject, render: bool = True) -> None:
        '''Removes the renderable visualization object from the scene.'''
        for actor in renderObject.actors(): self._renderer.RemoveActor(actor)
        if render: self.render()

    def setPickAction(
        self,
        onPicked: Callable[[Sequence[int], bool], None] | None,
        pickTarget: Literal['Points', 'Cells'] | None
    ) -> None:
        '''Sets the pick action on the current interaction style.'''
        self._interactionStyles[self._currentInteractionStyle].setPickAction(onPicked, pickTarget)

    def setView(self, view: Views, render: bool = True) -> None:
        '''Sets the camera view.'''
        focalPoint: tuple[float, float, float]
        position:   tuple[float, float, float]
        viewUp:     tuple[float, float, float]
        match view:
            case Views.Front:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+0.0, +0.0, +1.0)
                viewUp     = (+0.0, +1.0, +0.0)
            case Views.Back:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+0.0, +0.0, -1.0)
                viewUp     = (+0.0, +1.0, +0.0)
            case Views.Top:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+0.0, +1.0, +0.0)
                viewUp     = (+0.0, +0.0, -1.0)
            case Views.Bottom:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+0.0, -1.0, +0.0)
                viewUp     = (+0.0, +0.0, +1.0)
            case Views.Left:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (-1.0, +0.0, +0.0)
                viewUp     = (+0.0, +1.0, +0.0)
            case Views.Right:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+1.0, +0.0, +0.0)
                viewUp     = (+0.0, +1.0, +0.0)
            case Views.Isometric:
                focalPoint = (+0.0, +0.0, +0.0)
                position   = (+1.0, +1.0, +1.0)
                viewUp     = (+0.0, +1.0, +0.0)
        self._renderer.GetActiveCamera().SetFocalPoint(focalPoint)
        self._renderer.GetActiveCamera().SetPosition(position)
        self._renderer.GetActiveCamera().SetViewUp(viewUp)
        self._renderer.ResetCamera()
        if render: self.render()

    def setMeshRenderObject(self, mesh: Mesh | None, render: bool = True) -> None:
        '''Renders the specified mesh.'''
        if self._selectionRenderObject: self.remove(self._selectionRenderObject, render=False)
        if self._meshRenderObject: self.remove(self._meshRenderObject, render=False)
        self._meshRenderObject = MeshRenderObject(mesh) if mesh else None
        if self._meshRenderObject: self.add(self._meshRenderObject, render=False)
        if render: self.render()

    def setSelectionRenderObject(
        self,
        dataObject: NodeSet | ElementSet | ConcentratedLoad | BoundaryCondition | None,
        color: tuple[float, float, float] | None = None,
        modelDatabase: ModelDatabase | None = None,
        render: bool = True
    ) -> None:
        '''Renders the specified selection.'''
        if self._selectionRenderObject: self.remove(self._selectionRenderObject, render=False)
        if not self._meshRenderObject: return
        match dataObject:
            case NodeSet():
                self._selectionRenderObject = PointsRenderObject(
                    self._meshRenderObject.dataSet, dataObject.indices(), color
                )
            case ElementSet():
                self._selectionRenderObject = CellsRenderObject(
                    self._meshRenderObject.dataSet, dataObject.indices(), color
                )
            case ConcentratedLoad():
                if not modelDatabase: raise ValueError("missing optional argument: 'modelDatabase'")
                if sum(tuple(abs(x) for x in dataObject.components())) == 0.0:
                    self._selectionRenderObject = None
                else:
                    nodeSet: NodeSet = cast(NodeSet, modelDatabase.nodeSets[dataObject.nodeSetName])
                    origins: tuple[tuple[float, float, float], ...] = tuple(
                        modelDatabase.mesh.nodes[k].coordinates for k in nodeSet.indices()
                    )
                    self._selectionRenderObject = GroupRenderObject()
                    for i in range(3):
                        if dataObject.components()[i] == 0.0: continue
                        a: float = +1.0 if dataObject.components()[i] >= 0.0 else -1.0
                        directions: tuple[tuple[float, float, float], ...] = (
                            tuple(a if k == i else 0.0 for k in range(3)),
                        )*nodeSet.count
                        self._selectionRenderObject.add(ArrowsRenderObject(origins, directions, 'Normal', color))
            case BoundaryCondition():
                if not modelDatabase: raise ValueError("missing optional argument: 'modelDatabase'")
                if True not in dataObject.activeDOFs():
                    self._selectionRenderObject = None
                else:
                    nodeSet: NodeSet = cast(NodeSet, modelDatabase.nodeSets[dataObject.nodeSetName])
                    origins: tuple[tuple[float, float, float], ...] = tuple(
                        modelDatabase.mesh.nodes[k].coordinates for k in nodeSet.indices()
                    )
                    self._selectionRenderObject = GroupRenderObject()
                    for i in range(3):
                        if not dataObject.activeDOFs()[i]: continue
                        a: float = +1.0 if dataObject.components()[i] >= 0.0 else -1.0
                        directions: tuple[tuple[float, float, float], ...] = (
                            tuple(a if k == i else 0.0 for k in range(3)),
                        )*nodeSet.count
                        arrowType: str = 'Normal' if dataObject.components()[i] != 0.0 else 'NoShaft'
                        self._selectionRenderObject.add(ArrowsRenderObject(origins, directions, arrowType, color))
            case _:
                self._selectionRenderObject = None
        if self._selectionRenderObject:
            self.add(self._selectionRenderObject, render=False)
            InteractionStyle.recomputeGlyphSize(self._renderer)
        if render: self.render()
