from visualization.interaction.interactionStyle import InteractionStyle
from vtkmodules.vtkCommonCore import vtkObject

class PanInteractionStyle(InteractionStyle):
    '''
    Pan interactor style.
    '''

    # attribute slots
    __slots__ = ()

    def __init__(self) -> None:
        '''Pan interaction style constructor.'''
        super().__init__()

    def onLeftButtonPress(self, sender: vtkObject, event: str) -> None:
        '''On left button press.'''
        super().onMiddleButtonPress(sender, event)

    def onLeftButtonRelease(self, sender: vtkObject, event: str) -> None:
        '''On left button release.'''
        super().onMiddleButtonRelease(sender, event)
