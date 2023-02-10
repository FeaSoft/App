import math
import visualization.utility as vu
from typing import Literal
from visualization.interaction.interactionStyle import InteractionStyle
from vtkmodules.vtkCommonCore import vtkObject, vtkIdList, vtkDataArray
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid
from vtkmodules.vtkRenderingCore import vtkActor

class ProbeInteractionStyle(InteractionStyle):
    '''
    Probe point or cell interaction style.
    '''

    # attribute slots
    __slots__ = ('_pickedIndex', '_pickedDataSet', '_target')

    def __init__(self) -> None:
        '''Probe interaction style constructor.'''
        super().__init__()
        self._pickedIndex: int = -1
        self._pickedDataSet: vtkUnstructuredGrid | None = None
        self._target: Literal['Points', 'Cells'] | None = None

    def onLeftButtonPress(self, sender: vtkObject, event: str) -> None:
        '''On left button press.'''
        if self._isMiddleButtonDown or self._isRightButtonDown: return
        if self._pickedIndex > -1 and self._pickedDataSet and self._target:
            if self._target == 'Points':
                print(f'Node {self._pickedIndex + 1} (1-based indexing):')
                coordinates: tuple[float, float, float] = self._pickedDataSet.GetPoint(self._pickedIndex)
                print(' '*4 + 'Coordinates: ' + str(coordinates))
                pointData: vtkDataArray | None = self._pickedDataSet.GetPointData().GetScalars() # type: ignore
                if pointData:
                    scalar: float = pointData.GetTuple1(self._pickedIndex)
                    if not math.isnan(scalar): print(' '*4 + 'Scalar: ' + str(scalar))
            else:
                print(f'Element {self._pickedIndex + 1} (1-based indexing):')
                centroid: tuple[float, float, float] = vu.computeCentroid(
                    self._pickedDataSet.GetCell(self._pickedIndex)
                )
                print(' '*4 + 'Centroid: ' + str(centroid))
                idList: vtkIdList = self._pickedDataSet.GetCell(self._pickedIndex).GetPointIds() # type: ignore
                connectivity: tuple[int] = tuple(idList.GetId(i) + 1 for i in range(idList.GetNumberOfIds()))
                print(' '*4 + 'Connectivity: ' + str(connectivity))
                cellData: vtkDataArray | None = self._pickedDataSet.GetCellData().GetScalars() # type: ignore
                if cellData:
                    scalar: float = cellData.GetTuple1(self._pickedIndex)
                    if not math.isnan(scalar): print(' '*4 + 'Scalar: ' + str(scalar))

    def onLeftButtonRelease(self, sender: vtkObject, event: str) -> None:
        '''On left button release.'''
        pass

    def onMouseMove(self, sender: vtkObject, event: str) -> None:
        '''On mouse move.'''
        if not self._isLeftButtonDown and not self._isMiddleButtonDown and not self._isRightButtonDown:
            position: tuple[int, int] = self._interactor.GetEventPosition()
            self._pickedIndex, self._pickedDataSet = self.pickSingle(position, 'Points', self._renderer)
            if self._pickedDataSet:
                self._target = 'Points'
            else:
                self._pickedIndex, self._pickedDataSet = self.pickSingle(position, 'Cells', self._renderer)
                if self._pickedDataSet: self._target = 'Cells'
                else: self._target = None
            if self._pickedDataSet and self._target:
                if self._target == 'Points':
                    actor: vtkActor = self.newPointsHint(self._pickedDataSet, (self._pickedIndex,))
                else:
                    actor: vtkActor = self.newCellsHint(self._pickedDataSet, (self._pickedIndex,))
                    actor.GetProperty().SetRepresentationToWireframe()
                self._renderer.AddActor(actor)
                self.recomputeGlyphSize(self._renderer)
                self._renderWindow.Render()
                self._renderer.RemoveActor(actor)
            else:
                self._renderWindow.Render()
            self._base.OnMouseMove()
        else: super().onMouseMove(sender, event)
