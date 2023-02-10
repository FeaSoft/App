import vtkmodules.vtkRenderingContextOpenGL2 # type: ignore (initialize VTK)
from typing import Literal, Any, cast
from collections.abc import Callable, Sequence
from dataModel import Mesh, NodeSet, ElementSet, ConcentratedLoad, BoundaryCondition, ModelDatabase
from visualization.decoration import Triad, Info, ScalarBar
from visualization.rendering import (
    RenderObject, GridRenderObject, PointsRenderObject, CellsRenderObject, ArrowsRenderObject, GroupRenderObject
)
from visualization.interaction import (
    Views, InteractionStyles, InteractionStyle, RotateInteractionStyle, PanInteractionStyle, ZoomInteractionStyle,
    PickSingleInteractionStyle, PickMultipleInteractionStyle, ProbeInteractionStyle, RulerInteractionStyle
)
from PySide6.QtWidgets import QWidget, QFrame, QVBoxLayout
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor # type: ignore
from vtkmodules.vtkCommonCore import vtkObject
from vtkmodules.vtkRenderingCore import vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor

class Viewport(QFrame):
    '''
    Visualization viewport based on VTK.
    '''

    # class variables
    _callbacks: dict[int, Callable[[str, Any], None]] = {}
    _viewports: list['Viewport'] = []
    _currentInteractionStyle: InteractionStyles = InteractionStyles.Rotate
    _lineVisibility: bool = True

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
            viewport._interactor.SetInteractorStyle(viewport._interactionStyles[cls._currentInteractionStyle].base)
            viewport._interactor.RemoveObservers('CharEvent')
        cls.notifyOptionChanged('InteractionStyle', cls._currentInteractionStyle)

    @classmethod
    def lineVisibility(cls) -> bool:
        '''Gets the grid line visibility.'''
        return cls._lineVisibility

    @classmethod
    def setLineVisibility(cls, value: bool) -> None:
        '''Sets the grid line visibility.'''
        cls._lineVisibility = value
        for viewport in cls._viewports:
            if viewport._gridRenderObject:
                viewport._gridRenderObject.setLineVisibility(cls._lineVisibility)
            if isinstance(viewport._selectionRenderObject, CellsRenderObject):
                viewport._selectionRenderObject.setLineVisibility(cls._lineVisibility)
            viewport.render()
        cls.notifyOptionChanged('LineVisibility', cls._lineVisibility)

    @classmethod
    def setPickAction(
        cls,
        onPicked: Callable[[Sequence[int], bool], None] | None,
        pickTarget: Literal['Points', 'Cells'] | None
    ) -> None:
        '''Sets the pick action on the current interaction style.'''
        for viewport in cls._viewports:
            viewport._interactionStyles[cls._currentInteractionStyle].setPickAction(onPicked, pickTarget)

    @property
    def info(self) -> Info:
        '''The viewport information object.'''
        return self._info

    # attribute slots
    __slots__ = (
        '_layout', '_vtkWidget', '_renderer', '_renderWindow', '_interactor', '_interactionStyles', '_triad', '_info',
        '_scalarBar', '_gridRenderObject', '_selectionRenderObject'
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        '''Viewport constructor.'''
        super().__init__(parent)
        vtkObject.GlobalWarningDisplayOn()
        # self (frame)
        self.setStyleSheet('border: 1px solid rgb(185,185,185);')
        # layout
        self._layout: QVBoxLayout = QVBoxLayout(self)
        self._layout.setContentsMargins(0, 0, 0, 0)
        self._layout.setSpacing(0)
        self.setLayout(self._layout)
        # VTK widget
        self._vtkWidget: QVTKRenderWindowInteractor = QVTKRenderWindowInteractor(self)
        self._layout.addWidget(self._vtkWidget)
        # register viewport
        self._viewports.append(self)
        # renderer
        self._renderer: vtkRenderer = vtkRenderer()
        self._renderer.GradientBackgroundOn()
        self._renderer.SetBackground(0.6, 0.7, 0.8)
        self._renderer.SetBackground2(0.1, 0.2, 0.3)
        # render window
        self._renderWindow: vtkRenderWindow = cast(vtkRenderWindow, self._vtkWidget.GetRenderWindow())
        self._renderWindow.AddRenderer(self._renderer)
        # interactor
        self._interactor: vtkRenderWindowInteractor = self._renderWindow.GetInteractor()
        # interactor styles
        self._interactionStyles: dict[InteractionStyles, InteractionStyle] = {
            InteractionStyles.Rotate       : RotateInteractionStyle(),
            InteractionStyles.Pan          : PanInteractionStyle(),
            InteractionStyles.Zoom         : ZoomInteractionStyle(),
            InteractionStyles.PickSingle   : PickSingleInteractionStyle(),
            InteractionStyles.PickMultiple : PickMultipleInteractionStyle(),
            InteractionStyles.Probe        : ProbeInteractionStyle(),
            InteractionStyles.Ruler        : RulerInteractionStyle()
        }
        # triad & info % scalar bar
        self._triad: Triad = Triad()
        self._info: Info = Info()
        self._scalarBar: ScalarBar = ScalarBar()
        # render objects
        self._gridRenderObject: GridRenderObject | None = None
        self._selectionRenderObject: RenderObject | None = None

    def initialize(self) -> None:
        '''Initializes the viewport.'''
        self._interactor.Initialize()
        self._triad.initialize(self._interactor)
        self._info.initialize(self._renderer)
        self._scalarBar.initialize(self._renderer)
        self._scalarBar.setVisible(False)
        self.setInteractionStyle(self._currentInteractionStyle)

    def finalize(self) -> None:
        '''Finalizes the viewport.'''
        self._vtkWidget.Finalize()

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
        InteractionStyle.recomputeGlyphSize(self._renderer, render=False)
        if render: self.render()

    def setGridRenderObject(self, mesh: Mesh | None, isDeformable: bool, render: bool = True) -> None:
        '''Renders the specified grid.'''
        self._scalarBar.setVisible(False)
        if self._selectionRenderObject: self.remove(self._selectionRenderObject, render=False)
        if self._gridRenderObject: self.remove(self._gridRenderObject, render=False)
        self._gridRenderObject = GridRenderObject(
            mesh,
            isDeformable,
            self._scalarBar.lookupTable,
            self._lineVisibility
        ) if mesh else None
        if self._gridRenderObject: self.add(self._gridRenderObject, render=False)
        if render: self.render()

    def setGridDeformation(
        self,
        nodalDisplacements: tuple[tuple[float, float, float], ...] | None,
        render: bool = True
    ) -> None:
        '''Sets the deformation on the currently drawn grid.'''
        if not self._gridRenderObject: return
        if not nodalDisplacements:
            nodalDisplacements = tuple(
                (0.0, 0.0, 0.0) for _ in range(self._gridRenderObject.dataSet.GetNumberOfPoints())
            )
        self._gridRenderObject.setPointDisplacements(nodalDisplacements)
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
        if not self._gridRenderObject: return
        match dataObject:
            case NodeSet():
                self._selectionRenderObject = PointsRenderObject(
                    self._gridRenderObject.dataSet, dataObject.indices(), color
                )
            case ElementSet():
                self._selectionRenderObject = CellsRenderObject(
                    self._gridRenderObject.dataSet, dataObject.indices(), self._lineVisibility, color
                )
            case ConcentratedLoad():
                if not modelDatabase: raise ValueError("missing optional argument: 'modelDatabase'")
                if sum(abs(x) for x in dataObject.components()) == 0.0:
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
            InteractionStyle.recomputeGlyphSize(self._renderer, render=False)
        if render: self.render()

    def plotNodalScalarField(self, nodalScalarField: tuple[float, ...] | None, render: bool = True) -> None:
        '''Plots the given nodal scalar field on the current mesh.'''
        if not self._gridRenderObject:
            self._scalarBar.setVisible(False)
        else:
            self._gridRenderObject.setNodalScalarField(nodalScalarField)
            self._scalarBar.setVisible(nodalScalarField is not None)
        if render: self.render()
