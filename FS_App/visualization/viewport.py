import vtkmodules.vtkRenderingContextOpenGL2 # type: ignore (initialize VTK)
import visualization.preferences as vp
from typing import cast
from visualization.decorations import Triad
from visualization.interaction import InteractionStyles, InteractionStyle, RotateInteractionStyle
from PySide6.QtWidgets import QWidget
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor # type: ignore
from vtkmodules.vtkRenderingCore import vtkRenderer, vtkRenderWindow, vtkRenderWindowInteractor

class Viewport(QVTKRenderWindowInteractor):
    '''
    Visualization viewport based on VTK.
    '''

    # attribute slots
    __slots__ = ('_renderer', '_renderWindow', '_interactor', '_interactionStyles', '_triad')

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

    def initialize(self, interactionStyle: InteractionStyles) -> None:
        '''Initializes the viewport.'''
        self._interactor.Initialize()
        self._triad.initialize(self._interactor)
        self.setInteractionStyle(interactionStyle)

    def setInteractionStyle(self, interactionStyle: InteractionStyles) -> None:
        '''Sets the viewport interaction style.'''
        self._interactor.SetInteractorStyle(self._interactionStyles[interactionStyle].base)
        self._interactor.RemoveObservers('CharEvent')
