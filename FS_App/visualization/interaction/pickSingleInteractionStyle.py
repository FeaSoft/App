from visualization.interaction.interactionStyle import InteractionStyle
from vtkmodules.vtkCommonCore import vtkObject
from vtkmodules.vtkRenderingCore import vtkActor

class PickSingleInteractionStyle(InteractionStyle):
    '''
    Pick single point or cell interaction style.
    '''

    # attribute slots
    __slots__ = ('_isShiftKeyDown', '_pickedIndex')

    def __init__(self) -> None:
        '''Pick single interaction style constructor.'''
        super().__init__()
        self._isShiftKeyDown: bool = False
        self._pickedIndex: int = -1

    def onLeftButtonPress(self, sender: vtkObject, event: str) -> None:
        '''On left button press.'''
        if self._isMiddleButtonDown or self._isRightButtonDown: return
        self._isLeftButtonDown = True
        self._isShiftKeyDown = self._interactor.GetShiftKey() != 0
        if self._pickedIndex > -1 and self._onPicked:
            self._onPicked((self._pickedIndex,), self._isShiftKeyDown)

    def onLeftButtonRelease(self, sender: vtkObject, event: str) -> None:
        '''On left button release.'''
        self._isLeftButtonDown, self._isShiftKeyDown = False, False

    def onMouseMove(self, sender: vtkObject, event: str) -> None:
        '''On mouse move.'''
        if (
            not self._isLeftButtonDown and not self._isMiddleButtonDown and not self._isRightButtonDown
            and self._onPicked and self._pickTarget
        ):
            position: tuple[int, int] = self._interactor.GetEventPosition()
            self._pickedIndex, selection = self.pickSingle(position, self._pickTarget, self._renderer)
            if selection:
                if self._pickTarget == 'Points':
                    actor: vtkActor = self.newPointsHint(selection, (self._pickedIndex,))
                else:
                    actor: vtkActor = self.newCellsHint(selection, (self._pickedIndex,))
                    actor.GetProperty().SetRepresentationToWireframe()
                self._renderer.AddActor(actor)
                self.recomputeGlyphSize(self._renderer)
                self._renderWindow.Render()
                self._renderer.RemoveActor(actor)
            else:
                self._renderWindow.Render()
            self._base.OnMouseMove()
        else: super().onMouseMove(sender, event)
