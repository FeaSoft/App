import math
from visualization.interaction.interactionStyle import InteractionStyle
from vtkmodules.vtkCommonCore import vtkObject
from vtkmodules.vtkCommonDataModel import vtkUnstructuredGrid
from vtkmodules.vtkRenderingCore import vtkActor

class RulerInteractionStyle(InteractionStyle):
    '''
    Ruler (measure distance) interaction style.
    '''

    # attribute slots
    __slots__ = ('_pickedIndexA', '_pickedIndexB', '_pickedDataSet', '_hintPointA', '_hintPointB', '_hintLine')

    def __init__(self) -> None:
        '''Ruler interaction style constructor.'''
        super().__init__()
        self._pickedIndexA: int = -1
        self._pickedIndexB: int = -1
        self._pickedDataSet: vtkUnstructuredGrid | None = None
        self._hintPointA: vtkActor | None = None
        self._hintPointB: vtkActor | None = None
        self._hintLine: vtkActor | None = None

    def onLeftButtonPress(self, sender: vtkObject, event: str) -> None:
        '''On left button press.'''
        if self._isMiddleButtonDown or self._isRightButtonDown: return
        self._isLeftButtonDown = True

    def onLeftButtonRelease(self, sender: vtkObject, event: str) -> None:
        '''On left button release.'''
        self._isLeftButtonDown = False
        if self._hintPointA: self._renderer.RemoveActor(self._hintPointA)
        if self._hintPointB: self._renderer.RemoveActor(self._hintPointB)
        if self._hintLine: self._renderer.RemoveActor(self._hintLine)
        if (
            self._pickedIndexA > -1 and self._pickedIndexB > -1 and self._pickedDataSet
            and self._pickedIndexA != self._pickedIndexB
        ):
            coordinatesA: tuple[float, float, float] = self._pickedDataSet.GetPoint(self._pickedIndexA)
            coordinatesB: tuple[float, float, float] = self._pickedDataSet.GetPoint(self._pickedIndexB)
            dx: float = coordinatesB[0] - coordinatesA[0]
            dy: float = coordinatesB[1] - coordinatesA[1]
            dz: float = coordinatesB[2] - coordinatesA[2]
            distance: float = math.sqrt(dx*dx + dy*dy + dz*dz)
            print(f'Distance between nodes {self._pickedIndexA + 1} and {self._pickedIndexB + 1} (1-based indexing):')
            print(' '*4 + 'Magnitude: ' + str(distance))
            print(' '*4 + 'Components: ' + str((dx, dy, dz)))

    def onMouseMove(self, sender: vtkObject, event: str) -> None:
        '''On mouse move.'''
        if self._isLeftButtonDown and self._pickedIndexA > -1 and self._pickedDataSet:
            if self._hintPointB: self._renderer.RemoveActor(self._hintPointB)
            if self._hintLine: self._renderer.RemoveActor(self._hintLine)
            self._pointB = self._interactor.GetEventPosition()
            self._pickedIndexB, _ = self.pickSingle(self._pointB, 'Points', self._renderer)
            if self._pickedIndexB > -1:
                coordinatesA: tuple[float, float, float] = self._pickedDataSet.GetPoint(self._pickedIndexA)
                coordinatesB: tuple[float, float, float] = self._pickedDataSet.GetPoint(self._pickedIndexB)
                self._hintPointB = self.newPointsHint(self._pickedDataSet, (self._pickedIndexB,))
                self._hintLine = self.newLineHint(coordinatesA, coordinatesB)
                self._renderer.AddActor(self._hintPointB)
                self._renderer.AddActor(self._hintLine)
                self.recomputeGlyphSize(self._renderer)
            self._renderWindow.Render()
            self._base.OnMouseMove()
        elif not self._isLeftButtonDown and not self._isMiddleButtonDown and not self._isRightButtonDown:
            self._pickedIndexB = -1
            if self._hintPointA: self._renderer.RemoveActor(self._hintPointA)
            self._pointA = self._interactor.GetEventPosition()
            self._pickedIndexA, self._pickedDataSet = self.pickSingle(self._pointA, 'Points', self._renderer)
            if self._pickedIndexA > -1 and self._pickedDataSet:
                self._hintPointA = self.newPointsHint(self._pickedDataSet, (self._pickedIndexA,))
                self._renderer.AddActor(self._hintPointA)
                self.recomputeGlyphSize(self._renderer)
            self._renderWindow.Render()
            self._base.OnMouseMove()
        else: super().onMouseMove(sender, event)
