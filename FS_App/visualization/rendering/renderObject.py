from abc import ABC, abstractmethod
from collections.abc import Sequence
from vtkmodules.vtkRenderingCore import vtkActor

class RenderObject(ABC):
    '''
    Abstract base class for a renderable visualization object.
    '''

    # attribute slots
    __slots__ = ()

    @abstractmethod
    def __init__(self) -> None:
        '''Render object constructor.'''
        super().__init__()

    @abstractmethod
    def actors(self) -> Sequence[vtkActor]:
        '''The renderable VTK actors.'''
        ...
