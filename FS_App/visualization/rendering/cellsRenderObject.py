from collections.abc import Sequence
from visualization.rendering.renderObject import RenderObject
from vtkmodules.vtkCommonCore import vtkIdTypeArray
from vtkmodules.vtkCommonDataModel import vtkSelectionNode, vtkSelection, vtkUnstructuredGrid
from vtkmodules.vtkFiltersExtraction import vtkExtractSelection
from vtkmodules.vtkRenderingCore import vtkDataSetMapper, vtkActor

class CellsRenderObject(RenderObject):
    '''
    Renderable cells.
    '''

    # attribute slots
    __slots__ = ('_indices', '_selectionNode', '_selection', '_extractionFilter', '_mapper', '_actor')

    def __init__(self, dataSet: vtkUnstructuredGrid, indices: Sequence[int]) -> None:
        '''Cells render object constructor.'''
        # indices
        self._indices: vtkIdTypeArray = vtkIdTypeArray()
        self._indices.SetNumberOfValues(len(indices))
        for i, index in enumerate(indices):
            self._indices.SetValue(i, index)
        # selection node
        self._selectionNode: vtkSelectionNode = vtkSelectionNode()
        self._selectionNode.SetFieldType(vtkSelectionNode.CELL)
        self._selectionNode.SetContentType(vtkSelectionNode.INDICES)
        self._selectionNode.SetSelectionList(self._indices) # type: ignore
        # selection
        self._selection: vtkSelection = vtkSelection()
        self._selection.AddNode(self._selectionNode)
        # extraction filter
        self._extractionFilter: vtkExtractSelection = vtkExtractSelection()
        self._extractionFilter.SetInputData(0, dataSet)         # type: ignore
        self._extractionFilter.SetInputData(1, self._selection) # type: ignore
        self._extractionFilter.Update()                         # type: ignore
        # mapper
        self._mapper: vtkDataSetMapper = vtkDataSetMapper()
        self._mapper.SetInputConnection(self._extractionFilter.GetOutputPort())
        self._mapper.Update() # type: ignore
        # actor
        self._actor: vtkActor = vtkActor()
        self._actor.SetMapper(self._mapper)
        self._actor.GetProperty().EdgeVisibilityOn()
        self._actor.GetProperty().SetLineWidth(1.5)
        self._actor.GetProperty().LightingOff()

    def actors(self) -> tuple[vtkActor, ...]:
        '''The renderable VTK actors.'''
        return (self._actor,)

    def setColor(self, color: tuple[float, float, float]) -> None:
        '''Sets the renderable object color.'''
        self._actor.GetProperty().SetColor(*color)
