from visualization.interaction.interactionStyle import InteractionStyle
from vtkmodules.vtkCommonCore import vtkObject

class RotateInteractionStyle(InteractionStyle):
    '''
    Rotate (or spin) interactor style.
    '''

    # attribute slots
    __slots__ = ('_isShiftKeyDown',)

    def __init__(self) -> None:
        '''Rotate interaction style constructor.'''
        super().__init__()
        self._isShiftKeyDown: bool = False

    def onLeftButtonPress(self, sender: vtkObject, event: str) -> None:
        '''On left button press.'''
        if self._isMiddleButtonDown or self._isRightButtonDown: return
        self._isLeftButtonDown = True
        self._isShiftKeyDown = self._interactor.GetShiftKey() != 0
        self._pointA = self._interactor.GetEventPosition()
        if self._isShiftKeyDown: self._base.StartSpin()
        else: self._base.StartRotate()

    def onLeftButtonRelease(self, sender: vtkObject, event: str) -> None:
        '''On left button release.'''
        self._isLeftButtonDown, self._isShiftKeyDown = False, False
        if self._hint2D: self._renderer.RemoveActor2D(self._hint2D)
        self._base.EndRotate()
        self._base.EndSpin()

    def onMouseMove(self, sender: vtkObject, event: str) -> None:
        '''On mouse move.'''
        if self._isLeftButtonDown and self._isShiftKeyDown:
            if self._hint2D: self._renderer.RemoveActor2D(self._hint2D)
            self._pointB = self._interactor.GetEventPosition()
            self._hint2D = self.newArcHint(self._pointA, self._pointB, self._renderWindow.GetSize())
            self._renderer.AddActor2D(self._hint2D)
            self._base.OnMouseMove()
        else: super().onMouseMove(sender, event)
