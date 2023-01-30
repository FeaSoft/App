import vtkmodules.vtkRenderingContextOpenGL2 # type: ignore (initialize VTK)
from typing import cast
from dataModel import Mesh, NodeSet, ElementSet
from visualization.decoration import Triad, Info
from visualization.rendering import RenderObject, MeshRenderObject, PointsRenderObject, CellsRenderObject
from visualization.interaction import Views, InteractionStyles, InteractionStyle, RotateInteractionStyle
from PySide6.QtWidgets import QWidget
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor # type: ignore
from vtkmodules.vtkRenderingCore import vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor

class Viewport(QVTKRenderWindowInteractor):
    '''
    Visualization viewport based on VTK.
    '''

    @property
    def info(self) -> Info:
        '''The viewport information object.'''
        return self._info

    # attribute slots
    __slots__ = (
        '_renderer', '_renderWindow', '_interactor', '_interactionStyles', '_triad', '_info', '_meshRenderObject',
        '_selectionRenderObject'
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        '''Viewport constructor.'''
        super().__init__(parent) # type: ignore
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
        # interaction styles
        self._interactionStyles: dict[InteractionStyles, InteractionStyle] = {
            InteractionStyles.Rotate: RotateInteractionStyle()
        }
        # triad & info
        self._triad: Triad = Triad()
        self._info: Info = Info()
        # render objects
        self._meshRenderObject: MeshRenderObject | None = None
        self._selectionRenderObject: RenderObject | None = None

    def initialize(self, interactionStyle: InteractionStyles) -> None:
        '''Initializes the viewport.'''
        self._interactor.Initialize()
        self._triad.initialize(self._interactor)
        self._info.initialize(self._renderer)
        self.setInteractionStyle(interactionStyle)

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

    def setInteractionStyle(self, interactionStyle: InteractionStyles) -> None:
        '''Sets the viewport interaction style.'''
        self._interactor.SetInteractorStyle(self._interactionStyles[interactionStyle].base)
        self._interactor.RemoveObservers('CharEvent')

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
        if self._meshRenderObject: self.remove(self._meshRenderObject, render=False)
        self._meshRenderObject = MeshRenderObject(mesh) if mesh else None
        if self._meshRenderObject: self.add(self._meshRenderObject, render=False)
        if render: self.render()

    def setSelectionRenderObject(
        self,
        dataObject: NodeSet | ElementSet | None,
        color: tuple[float, float, float] | None = None,
        render: bool = True
    ) -> None:
        '''Renders the specified selection.'''
        if self._selectionRenderObject: self.remove(self._selectionRenderObject, render=False)
        if not self._meshRenderObject: return
        match dataObject:
            case NodeSet():
                self._selectionRenderObject = PointsRenderObject(self._meshRenderObject, dataObject.indices())
            case ElementSet():
                self._selectionRenderObject = CellsRenderObject(self._meshRenderObject, dataObject.indices())
            case _:
                self._selectionRenderObject = None
        if self._selectionRenderObject:
            if color: self._selectionRenderObject.setColor(color)
            self.add(self._selectionRenderObject, render=False)
        if render: self.render()