from collections.abc import Sequence
from visualization.rendering.renderObject import RenderObject
from vtkmodules.vtkRenderingCore import vtkActor

class GroupRenderObject(RenderObject):
    '''
    Represents a group of renderable objects.
    '''

    # attribute slots
    __slots__ = ('_actors',)

    def __init__(self) -> None:
        '''Group render object constructor.'''
        super().__init__()
        self._actors: list[vtkActor] = []

    def add(self, renderObject: RenderObject) -> None:
        '''Adds the specified render object to the renderable group.'''
        for actor in renderObject.actors(): self._actors.append(actor)

    def actors(self) -> Sequence[vtkActor]:
        '''The renderable VTK actors.'''
        return self._actors
