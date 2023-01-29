import visualization.preferences as vp
from typing import Literal
from collections.abc import Sequence
from visualization.rendering.renderObject import RenderObject
from vtkmodules.vtkCommonCore import vtkIdTypeArray
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid, vtkSelectionNode, vtkSelection
from vtkmodules.vtkFiltersExtraction import vtkExtractSelection
from vtkmodules.vtkRenderingCore import vtkDataSetMapper, vtkActor

class IndexSetRenderObject(RenderObject):
    '''
    Index set renderable object.
    '''

    # attribute slots
    __slots__ = ('_indices', '_selectionNode', '_selection', '_extractionFilter', '_dataSetMapper', '_actor')

    def __init__(self, dataSet: vtkUnstructuredGrid) -> None:
        '''Index set render object constructor.'''
        # indices
        self._indices: vtkIdTypeArray = vtkIdTypeArray()
        # selection node
        self._selectionNode: vtkSelectionNode = vtkSelectionNode()
        self._selectionNode.SetFieldType(vtkSelectionNode.POINT)
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
        self._dataSetMapper: vtkDataSetMapper = vtkDataSetMapper()
        self._dataSetMapper.SetInputConnection(self._extractionFilter.GetOutputPort())
        self._dataSetMapper.ScalarVisibilityOff()
        self._dataSetMapper.Update() # type: ignore
        # actor
        self._actor: vtkActor = vtkActor()
        self._actor.SetMapper(self._dataSetMapper)
        self._actor.GetProperty().EdgeVisibilityOn()
        self._actor.GetProperty().SetEdgeColor(*vp.getMeshLineColor())
        self._actor.GetProperty().SetPointSize(vp.getSelectionPointSize())

    def actors(self) -> tuple[vtkActor, ...]:
        '''The renderable VTK actors.'''
        return (self._actor,)

    def update(
        self,
        indices: Sequence[int],
        target: Literal['Points', 'Cells'],
        color: tuple[float, float, float]
    ) -> None:
        '''Updates the selected indices.'''
        # update indices
        self._indices.SetNumberOfValues(len(indices))
        for i, index in enumerate(indices): self._indices.SetValue(i, index)
        self._indices.Modified()
        # update selection node
        self._selectionNode.SetFieldType(vtkSelectionNode.POINT if target == 'Points' else vtkSelectionNode.CELL)
        self._selectionNode.Modified()
        # update actor
        self._actor.GetProperty().SetColor(*color)
        self._actor.Modified()
