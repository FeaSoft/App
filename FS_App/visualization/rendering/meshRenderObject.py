import visualization.preferences as vp
from collections.abc import Sequence
from dataModel import Mesh
from visualization.rendering.renderObject import RenderObject
from visualization.rendering.indexSetRenderObject import IndexSetRenderObject
from vtkmodules.vtkCommonCore import vtkPoints, vtkLookupTable, vtkBitArray
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid
from vtkmodules.vtkRenderingCore import vtkDataSetMapper, vtkActor

class MeshRenderObject(RenderObject):
    '''
    Finite element mesh renderable object.
    '''

    @staticmethod
    def buildDataSet(mesh: Mesh) -> vtkUnstructuredGrid:
        '''Builds the vtkUnstructuredGrid data set object.'''
        # create the data set object
        dataSet: vtkUnstructuredGrid = vtkUnstructuredGrid()
        # set point coordinates
        points: vtkPoints = vtkPoints()
        points.SetNumberOfPoints(len(mesh.nodes))
        for i, node in enumerate(mesh.nodes):
            points.SetPoint(i, node.coordinates)
        dataSet.SetPoints(points) # type: ignore
        # set cell connectivity
        dataSet.AllocateEstimate(len(mesh.elements), 8)
        for element in mesh.elements:
            dataSet.InsertNextCell(element.cellType, element.nodeCount, element.nodeIndices) # type: ignore
        dataSet.Squeeze()
        # done
        return dataSet

    # attribute slots
    __slots__ = (
        '_dataSet', '_dataSetMapper', '_actor', '_lookupTable', '_cellSelectionFlags', '_selectionRenderObject'
    )

    def __init__(self, mesh: Mesh) -> None:
        '''Mesh render object constructor.'''
        super().__init__()
        # lookup table
        self._lookupTable: vtkLookupTable = vtkLookupTable()
        self._lookupTable.SetNumberOfColors(2)
        self._lookupTable.SetTableValue(0, *vp.getMeshCellColor(), 1.0)
        self._lookupTable.SetTableValue(1, 0.0, 0.0, 0.0, 1.0)
        self._lookupTable.Build()
        # cell selection flags
        self._cellSelectionFlags: vtkBitArray = vtkBitArray()
        self._cellSelectionFlags.SetNumberOfValues(len(mesh.elements))
        for i in range(len(mesh.elements)): self._cellSelectionFlags.SetValue(i, 0)
        # data set
        self._dataSet: vtkUnstructuredGrid = self.buildDataSet(mesh)
        self._dataSet.GetCellData().SetScalars(self._cellSelectionFlags) # type: ignore
        # data set mapper
        self._dataSetMapper: vtkDataSetMapper = vtkDataSetMapper()
        self._dataSetMapper.SetInputData(self._dataSet)       # type: ignore
        self._dataSetMapper.SetLookupTable(self._lookupTable) # type: ignore
        self._dataSetMapper.InterpolateScalarsBeforeMappingOn()
        self._dataSetMapper.ScalarVisibilityOn()
        self._dataSetMapper.SetScalarRange(0.0, 1.0)
        self._dataSetMapper.Update() # type: ignore
        # actor
        self._actor: vtkActor = vtkActor()
        self._actor.SetMapper(self._dataSetMapper)
        self._actor.GetProperty().SetColor(*vp.getMeshCellColor())
        self._actor.GetProperty().SetEdgeColor(*vp.getMeshLineColor())
        self._actor.GetProperty().SetEdgeVisibility(1 if vp.getMeshLineVisibility() else 0)
        # selection render object
        self._selectionRenderObject: IndexSetRenderObject = IndexSetRenderObject(self._dataSet)

    def actors(self) -> tuple[vtkActor, ...]:
        '''The renderable VTK actors.'''
        return (self._actor,) + self._selectionRenderObject.actors()

    def clearSelection(self) -> None:
        '''Clears the current selection.'''
        # clear cell selection flags
        for i in range(self._cellSelectionFlags.GetNumberOfValues()): self._cellSelectionFlags.SetValue(i, 0)
        self._cellSelectionFlags.Modified()
        # clear selection render object
        self._selectionRenderObject.update((), 'Points', (0.0, 0.0, 0.0))

    def selectPoints(self, indices: Sequence[int], color: tuple[float, float, float]) -> None:
        '''Selects/colors the specified points.'''
        self._selectionRenderObject.update(indices, 'Points', color)

    def selectCells(self, indices: Sequence[int], color: tuple[float, float, float]) -> None:
        '''Selects/colors the specified cells.'''
        # update lookup table
        self._lookupTable.SetTableValue(1, *color, 1.0)
        self._lookupTable.Modified()
        # update cell selection flags
        for index in indices: self._cellSelectionFlags.SetValue(index, 1)
        self._cellSelectionFlags.Modified()
        # update selection render object
        self._selectionRenderObject.update(indices, 'Cells', color)
