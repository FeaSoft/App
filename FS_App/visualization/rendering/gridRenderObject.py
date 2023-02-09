from typing import cast
from collections.abc import Sequence
from dataModel import Mesh
from visualization.rendering.renderObject import RenderObject
from vtkmodules.vtkCommonCore import vtkPoints, vtkDoubleArray, vtkLookupTable
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid
from vtkmodules.vtkRenderingCore import vtkDataSetMapper, vtkActor

class GridRenderObject(RenderObject):
    '''
    Renderable grid.
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
        # set point data
        pointData: vtkDoubleArray = vtkDoubleArray()
        pointData.SetNumberOfValues(len(mesh.nodes))
        dataSet.GetPointData().SetScalars(pointData) # type: ignore
        # done
        dataSet.Squeeze()
        return dataSet

    @property
    def dataSet(self) -> vtkUnstructuredGrid:
        '''The underlying VTK data set.'''
        return self._dataSet

    # attribute slots
    __slots__ = ('_dataSet', '_mapper', '_actor')

    def __init__(self, mesh: Mesh, lookupTable: vtkLookupTable) -> None:
        '''Mesh render object constructor.'''
        super().__init__()
        # data set
        self._dataSet: vtkUnstructuredGrid = self.buildDataSet(mesh)
        # mapper
        self._mapper: vtkDataSetMapper = vtkDataSetMapper()
        self._mapper.InterpolateScalarsBeforeMappingOn()
        self._mapper.ScalarVisibilityOff()
        self._mapper.SetLookupTable(lookupTable) # type: ignore
        self._mapper.SetInputData(self._dataSet) # type: ignore
        self._mapper.Update()                    # type: ignore
        # actor
        self._actor: vtkActor = vtkActor()
        self._actor.SetMapper(self._mapper)
        self._actor.GetProperty().EdgeVisibilityOn()
        self._actor.GetProperty().SetLineWidth(1.5)
        self._actor.GetProperty().SetColor(0.0, 0.5, 1.0)

    def actors(self) -> Sequence[vtkActor]:
        '''The renderable VTK actors.'''
        return (self._actor,)

    def setNodalScalarField(self, nodalScalarField: tuple[float, ...] | None) -> None:
        '''Sets the current nodal scalar field to be shown.'''
        if nodalScalarField:
            # update scalars
            scalars: vtkDoubleArray = cast(vtkDoubleArray, self._dataSet.GetPointData().GetScalars()) # type: ignore
            for i, scalar in enumerate(nodalScalarField):
                scalars.SetValue(i, scalar)
            scalars.Modified()
            # update mapper
            self._mapper.ScalarVisibilityOn()
            self._mapper.SetScalarRange(min(nodalScalarField), max(nodalScalarField))
            self._mapper.Modified()
        else:
            # update mapper
            self._mapper.ScalarVisibilityOff()
            self._mapper.Modified()
