from collections.abc import Sequence
from visualization.interaction.interactionStyle import InteractionStyle
from vtkmodules.vtkCommonCore import vtkObject

class PickMultipleInteractionStyle(InteractionStyle):
    '''
    Pick multiple points or cells interaction style.
    '''

    # attribute slots
    __slots__ = ()

    def __init__(self) -> None:
        '''Pick multiple interaction style constructor.'''
        super().__init__()

    def onLeftButtonPress(self, sender: vtkObject, event: str) -> None:
        '''On left button press.'''
        if self._isMiddleButtonDown or self._isRightButtonDown: return
        self._isLeftButtonDown = True
        self._pointA = self._interactor.GetEventPosition()

    def onLeftButtonRelease(self, sender: vtkObject, event: str) -> None:
        '''On left button release.'''
        self._isLeftButtonDown = False
        self._pointB = self._interactor.GetEventPosition()
        if self._hint2D:
            self._renderer.RemoveActor2D(self._hint2D)
            self._renderWindow.Render()
        if self._onPicked and self._pickTarget:
            remove: bool = self._interactor.GetShiftKey() != 0
            indices: Sequence[int] = self.pickMultiple(self._pointA, self._pointB, self._pickTarget, self._renderer)
            self._onPicked(indices, remove)

    def onMouseMove(self, sender: vtkObject, event: str) -> None:
        '''On mouse move.'''
        if self._isLeftButtonDown:
            if self._hint2D: self._renderer.RemoveActor2D(self._hint2D)
            self._pointB = self._interactor.GetEventPosition()
            self._hint2D = self.newRectangleHint(self._pointA, self._pointB)
            self._renderer.AddActor2D(self._hint2D)
            self._renderWindow.Render()
            self._base.OnMouseMove()
        else: super().onMouseMove(sender, event)
