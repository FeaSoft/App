import vtkmodules.vtkRenderingContextOpenGL2 # type: ignore (initialize VTK)
import visualization.preferences as vp
from typing import cast
from dataModel import Mesh
from visualization.decoration import Triad
from visualization.rendering import RenderObject, MeshRenderObject
from visualization.interaction import InteractionStyles, InteractionStyle, RotateInteractionStyle
from PySide6.QtWidgets import QWidget
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor # type: ignore
from vtkmodules.vtkRenderingCore import vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor

class Viewport(QVTKRenderWindowInteractor):
    '''
    Visualization viewport based on VTK.
    '''

    # attribute slots
    __slots__ = ('_renderer', '_renderWindow', '_interactor', '_interactionStyles', '_triad', '_meshRenderObject')

    def __init__(self, parent: QWidget | None = None) -> None:
        '''Viewport constructor.'''
        super().__init__(parent) # type: ignore
        # renderer
        self._renderer: vtkRenderer = vtkRenderer()
        self._renderer.GradientBackgroundOn()
        self._renderer.SetBackground(vp.getViewportBackground1())
        self._renderer.SetBackground2(vp.getViewportBackground2())
        # render window
        self._renderWindow: vtkRenderWindow = cast(vtkRenderWindow, self.GetRenderWindow())
        self._renderWindow.AddRenderer(self._renderer)
        # interactor
        self._interactor: vtkRenderWindowInteractor = self._renderWindow.GetInteractor()
        # interaction styles
        self._interactionStyles: dict[InteractionStyles, InteractionStyle] = {
            InteractionStyles.Rotate: RotateInteractionStyle()
        }
        # triad
        self._triad: Triad = Triad()
        # render objects
        self._meshRenderObject: MeshRenderObject | None = None

    def initialize(self, interactionStyle: InteractionStyles) -> None:
        '''Initializes the viewport.'''
        self._interactor.Initialize()
        self._triad.initialize(self._interactor)
        self.setInteractionStyle(interactionStyle)

    def render(self) -> None:
        '''Renders the current scene.'''
        self._renderWindow.Render()

    def add(self, renderObject: RenderObject, render: bool = True) -> None:
        '''Adds the renderable visualization object to the scene.'''
        for actor in renderObject.actors: self._renderer.AddActor(actor)
        if render: self.render()

    def remove(self, renderObject: RenderObject, render: bool = True) -> None:
        '''Removes the renderable visualization object from the scene.'''
        for actor in renderObject.actors: self._renderer.RemoveActor(actor)
        if render: self.render()

    def setInteractionStyle(self, interactionStyle: InteractionStyles) -> None:
        '''Sets the viewport interaction style.'''
        self._interactor.SetInteractorStyle(self._interactionStyles[interactionStyle].base)
        self._interactor.RemoveObservers('CharEvent')

    def setMesh(self, mesh: Mesh | None, render: bool = True) -> None:
        '''Renders the specified mesh.'''
        if self._meshRenderObject: self.remove(self._meshRenderObject, render=False)
        self._meshRenderObject = MeshRenderObject(mesh) if mesh else None
        if self._meshRenderObject: self.add(self._meshRenderObject, render=False)
        if render: self.render()
