from typing import Any
from visualization import Viewport
from application.optionsCommonDialog.optionsCommonDialogShell import OptionsCommonDialogShell
from PySide6.QtWidgets import QWidget, QColorDialog, QCheckBox
from PySide6.QtGui import QColor

class OptionsCommonDialog(OptionsCommonDialogShell):
    '''
    The options > common dialog.
    '''

    @staticmethod
    def setBoxColor(widget: QCheckBox, color: tuple[float, float, float]) -> None:
        '''Sets the box background color.'''
        rgb: tuple[int, int, int] = tuple(int(x*255) for x in color)
        widget.setStyleSheet(f'QCheckBox::indicator {{ background: rgb{rgb}; }}')
        widget.setText(str(rgb))

    @staticmethod
    def boxColor(widget: QCheckBox) -> tuple[int, int, int]:
        '''Gets the box background color.'''
        return tuple(int(x) for x in widget.styleSheet().split('(')[1].split(')')[0].replace(' ', '').split(','))

    @staticmethod
    def convertColor(color: QColor) -> tuple[float, float, float]:
        '''Converts QColor to RGB tuple.'''
        return (color.red()/255.0, color.green()/255.0, color.blue()/255.0)

    # attribute slots
    __slots__ = ()

    def __init__(self, parent: QWidget | None = None) -> None:
        '''Options > common dialog constructor.'''
        super().__init__(parent)
        # initial setup
        self._gridLinesVisibleBox.setChecked(Viewport.gridLinesVisible())
        self._gridLineWidthBox.setValue(Viewport.gridLineWidth())
        self.setBoxColor(self._gridLineColorBox, Viewport.gridLineColor())
        self._cellRepresentationBox.setCurrentText(Viewport.gridCellRepresentation())
        self.setBoxColor(self._cellColorBox, Viewport.gridCellColor())
        self._pointScaleBox.setValue(Viewport.pointGlyphScale())
        self._arrowScaleBox.setValue(Viewport.arrowGlyphScale())
        self._projectionBox.setCurrentText(Viewport.projection())
        self._lightingBox.setCurrentText(Viewport.lighting())
        self.setBoxColor(self._background1Box, Viewport.background1())
        self.setBoxColor(self._background2Box, Viewport.background2())
        # setup connections
        Viewport.registerCallback(self.onViewportOptionChanged)
        self._gridLinesVisibleBox.stateChanged.connect(self.onGridLinesVisible)            # type: ignore
        self._gridLineWidthBox.valueChanged.connect(self.onGridLineWidth)                  # type: ignore
        self._gridLineColorBox.clicked.connect(self.onGridLineColor)                       # type: ignore
        self._cellRepresentationBox.currentIndexChanged.connect(self.onCellRepresentation) # type: ignore
        self._cellColorBox.clicked.connect(self.onCellColor)                               # type: ignore
        self._pointScaleBox.valueChanged.connect(self.onPointScale)                        # type: ignore
        self._arrowScaleBox.valueChanged.connect(self.onArrowScale)                        # type: ignore
        self._projectionBox.currentIndexChanged.connect(self.onProjection)                 # type: ignore
        self._lightingBox.currentIndexChanged.connect(self.onLighting)                     # type: ignore
        self._background1Box.clicked.connect(self.onBackground1)                           # type: ignore
        self._background2Box.clicked.connect(self.onBackground2)                           # type: ignore

    def getColor(self, widget: QCheckBox) -> QColor:
        '''Launches the QColorDialog.'''
        return QColorDialog.getColor(
            parent=self,
            initial=QColor(*self.boxColor(widget)),
            options=QColorDialog.ColorDialogOption.DontUseNativeDialog
        )

    def onViewportOptionChanged(self, optionName: str, optionValue: Any) -> None:
        '''On viewport global option changed.'''
        match optionName:
            case 'GridLinesVisible': self._gridLinesVisibleBox.setChecked(optionValue)
            case 'GridLineWidth': self._gridLineWidthBox.setValue(optionValue)
            case 'GridLineColor': self.setBoxColor(self._gridLineColorBox, optionValue)
            case 'GridCellRepresentation': self._cellRepresentationBox.setCurrentText(optionValue)
            case 'GridCellColor': self.setBoxColor(self._cellColorBox, optionValue)
            case 'PointGlyphScale': self._pointScaleBox.setValue(optionValue)
            case 'ArrowGlyphScale': self._arrowScaleBox.setValue(optionValue)
            case 'Projection': self._projectionBox.setCurrentText(optionValue)
            case 'Lighting': self._lightingBox.setCurrentText(optionValue)
            case 'Background1': self.setBoxColor(self._background1Box, Viewport.background1())
            case 'Background2': self.setBoxColor(self._background2Box, Viewport.background2())
            case _: pass

    def onGridLinesVisible(self) -> None:
        '''On grid lines visible box state changed.'''
        Viewport.setGridLinesVisible(self._gridLinesVisibleBox.isChecked())

    def onGridLineWidth(self) -> None:
        '''On grid line width box value changed.'''
        Viewport.setGridLineWidth(self._gridLineWidthBox.value())

    def onGridLineColor(self) -> None:
        '''On grid line color box clicked.'''
        color: QColor = self.getColor(self._gridLineColorBox)
        if color.isValid(): Viewport.setGridLineColor(self.convertColor(color))

    def onCellRepresentation(self) -> None:
        '''On cell representation box current index changed.'''
        Viewport.setGridCellRepresentation(self._cellRepresentationBox.currentText()) # type: ignore

    def onCellColor(self) -> None:
        '''On cell color box clicked.'''
        color: QColor = self.getColor(self._cellColorBox)
        if color.isValid(): Viewport.setGridCellColor(self.convertColor(color))

    def onPointScale(self) -> None:
        '''On point scale box value changed.'''
        Viewport.setPointGlyphScale(self._pointScaleBox.value())

    def onArrowScale(self) -> None:
        '''On arrow scale box value changed.'''
        Viewport.setArrowGlyphScale(self._arrowScaleBox.value())

    def onProjection(self) -> None:
        '''On projection box current index changed.'''
        Viewport.setProjection(self._projectionBox.currentText()) # type: ignore

    def onLighting(self) -> None:
        '''On lighting box current index changed.'''
        Viewport.setLighting(self._lightingBox.currentText()) # type: ignore

    def onBackground1(self) -> None:
        '''On background 1 box clicked.'''
        color: QColor = self.getColor(self._background1Box)
        if color.isValid(): Viewport.setBackground1(self.convertColor(color))

    def onBackground2(self) -> None:
        '''On background 2 box clicked.'''
        color: QColor = self.getColor(self._background2Box)
        if color.isValid(): Viewport.setBackground2(self.convertColor(color))
        






