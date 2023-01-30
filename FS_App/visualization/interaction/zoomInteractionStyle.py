from visualization.interaction.interactionStyle import InteractionStyle
from vtkmodules.vtkCommonCore import vtkObject

class ZoomInteractionStyle(InteractionStyle):
    '''
    Zoom interactor style.
    '''

    # attribute slots
    __slots__ = ()

    def __init__(self) -> None:
        '''Zoom interaction style constructor.'''
        super().__init__()

    def onLeftButtonPress(self, sender: vtkObject, event: str) -> None:
        '''On left button press.'''
        super().onRightButtonPress(sender, event)

    def onLeftButtonRelease(self, sender: vtkObject, event: str) -> None:
        '''On left button release.'''
        super().onRightButtonRelease(sender, event)
