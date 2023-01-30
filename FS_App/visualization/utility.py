from collections.abc import Sequence
from vtkmodules.vtkCommonCore import vtkPoints
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid, vtkCell

def findPointIndices(dataSet: vtkUnstructuredGrid, points: vtkUnstructuredGrid) -> Sequence[int]:
    '''Finds the indices of the given points.'''
    # build lookup dictionary (key: coordinates, value: index)
    lookup: dict[tuple[float, float, float], int] = {}
    for i in range(dataSet.GetNumberOfPoints()):
        coordinates: tuple[float, float, float] = dataSet.GetPoint(i)
        lookup[coordinates] = i
    # perform lookup (get indices based on coordinates)
    indices: list[int] = [0]*points.GetNumberOfPoints()
    for i in range(points.GetNumberOfPoints()):
        coordinates: tuple[float, float, float] = points.GetPoint(i)
        indices[i] = lookup[coordinates]
    # done
    return indices

def findCellIndices(dataSet: vtkUnstructuredGrid, cells: vtkUnstructuredGrid) -> Sequence[int]:
    '''Finds the indices of the given cells.'''
    # build lookup dictionary (key: centroid, value: index)
    lookup: dict[tuple[float, float, float], int] = {}
    for i in range(dataSet.GetNumberOfCells()):
        centroid: tuple[float, float, float] = computeCentroid(dataSet.GetCell(i))
        lookup[centroid] = i
    # perform lookup (get indices based on centroid)
    indices: list[int] = [0]*cells.GetNumberOfCells()
    for i in range(cells.GetNumberOfCells()):
        centroid: tuple[float, float, float] = computeCentroid(cells.GetCell(i))
        indices[i] = lookup[centroid]
    # done
    return indices

def computeCentroid(cell: vtkCell) -> tuple[float, float, float]:
    '''Computes the centroid of the given cell.'''
    points: vtkPoints = cell.GetPoints() # type: ignore
    n: int = points.GetNumberOfPoints()
    xc, yc, zc = 0.0, 0.0, 0.0
    for i in range(n):
        x, y, z = points.GetPoint(i)
        xc += x; yc += y; zc += z
    xc /= n; yc /= n; zc /= n
    return xc, yc, zc
