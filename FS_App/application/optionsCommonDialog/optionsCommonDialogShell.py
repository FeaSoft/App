from PySide6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QGridLayout, QGroupBox, QLabel, QCheckBox, QDoubleSpinBox, QComboBox, QSpinBox
)

class OptionsCommonDialogShell(QDialog):
    '''
    The options > common dialog shell (basic UI).
    '''

#   # attribute slots (crashes QT)
#   __slots__ = (
#       '_layout', '_gridLinesGroupBox', '_gridLinesGroupBoxLayout', '_gridLinesVisibleLabel', '_gridLinesVisibleBox',
#       '_gridLineWidthLabel', '_gridLineWidthBox', '_gridLineColorLabel', '_gridLineColorBox', '_gridCellsGroupBox',
#       '_gridCellsGroupBoxLayout', '_cellRepresentationLabel', '_cellRepresentationBox', '_cellColorLabel',
#       '_cellColorBox', '_gridGlyphsGroupBox', '_gridGlyphsGroupBoxLayout', '_pointScaleLabel', '_pointScaleBox',
#       '_arrowScaleLabel', '_arrowScaleBox', '_viewportGroupBox', '_viewportGroupBoxLayout', '_projectionLabel',
#       '_projectionBox', '_lightingLabel', '_lightingBox', '_backgroundLabel', '_background1Box', '_background2Box',
#       '_foregroundLabel', '_foregroundBox', '_fontSizeLabel', '_fontSizeBox'
#   )

    def __init__(self, parent: QWidget | None = None) -> None:
        '''Options > common dialog shell constructor.'''
        super().__init__(parent)

        # dialog (self)
        self.setWindowTitle('Common Options')
        self.resize(300, 0)

        # layout
        self._layout: QVBoxLayout = QVBoxLayout(self)
        self.setLayout(self._layout)

        # grid lines group box
        self._gridLinesGroupBox: QGroupBox = QGroupBox(self)
        self._gridLinesGroupBox.setTitle('Grid Lines')
        self._layout.addWidget(self._gridLinesGroupBox)

        # grid lines group box layout
        self._gridLinesGroupBoxLayout: QGridLayout = QGridLayout(self._gridLinesGroupBox)
        self._gridLinesGroupBox.setLayout(self._gridLinesGroupBoxLayout)

        # grid lines visible label
        self._gridLinesVisibleLabel: QLabel = QLabel(self._gridLinesGroupBox)
        self._gridLinesVisibleLabel.setText('Line Visibility:')
        self._gridLinesGroupBoxLayout.addWidget(self._gridLinesVisibleLabel, 0, 0)

        # grid lines visible box
        self._gridLinesVisibleBox: QCheckBox = QCheckBox(self._gridLinesGroupBox)
        self._gridLinesGroupBoxLayout.addWidget(self._gridLinesVisibleBox, 0, 1)

        # grid line width label
        self._gridLineWidthLabel: QLabel = QLabel(self._gridLinesGroupBox)
        self._gridLineWidthLabel.setText('Line Width:')
        self._gridLinesGroupBoxLayout.addWidget(self._gridLineWidthLabel, 1, 0)

        # grid line width slider
        self._gridLineWidthBox: QDoubleSpinBox = QDoubleSpinBox(self._gridLinesGroupBox)
        self._gridLineWidthBox.setDecimals(1)
        self._gridLineWidthBox.setMinimum(1.0)
        self._gridLineWidthBox.setMaximum(10.0)
        self._gridLineWidthBox.setSingleStep(0.5)
        self._gridLinesGroupBoxLayout.addWidget(self._gridLineWidthBox, 1, 1)

        # grid line color label
        self._gridLineColorLabel: QLabel = QLabel(self._gridLinesGroupBox)
        self._gridLineColorLabel.setText('Line Color:')
        self._gridLinesGroupBoxLayout.addWidget(self._gridLineColorLabel, 2, 0)

        # grid line color box
        self._gridLineColorBox: QCheckBox = QCheckBox(self._gridLinesGroupBox)
        self._gridLineColorBox.setCheckable(False)
        self._gridLinesGroupBoxLayout.addWidget(self._gridLineColorBox, 2, 1)

        # grid cells group box
        self._gridCellsGroupBox: QGroupBox = QGroupBox(self)
        self._gridCellsGroupBox.setTitle('Grid Cells')
        self._layout.addWidget(self._gridCellsGroupBox)

        # grid cells group box layout
        self._gridCellsGroupBoxLayout: QGridLayout = QGridLayout(self._gridCellsGroupBox)
        self._gridCellsGroupBox.setLayout(self._gridCellsGroupBoxLayout)

        # cell representation label
        self._cellRepresentationLabel: QLabel = QLabel(self._gridCellsGroupBox)
        self._cellRepresentationLabel.setText('Cell Representation:')
        self._gridCellsGroupBoxLayout.addWidget(self._cellRepresentationLabel, 0, 0)

        # cell representation box
        self._cellRepresentationBox: QComboBox = QComboBox(self._gridCellsGroupBox)
        self._cellRepresentationBox.addItems(('Surface', 'Wireframe'))
        self._gridCellsGroupBoxLayout.addWidget(self._cellRepresentationBox, 0, 1)

        # cell color label
        self._cellColorLabel: QLabel = QLabel(self._gridCellsGroupBox)
        self._cellColorLabel.setText('Cell Color:')
        self._gridCellsGroupBoxLayout.addWidget(self._cellColorLabel, 1, 0)

        # cell color box
        self._cellColorBox: QCheckBox = QCheckBox(self._gridCellsGroupBox)
        self._cellColorBox.setCheckable(False)
        self._gridCellsGroupBoxLayout.addWidget(self._cellColorBox, 1, 1)

        # grid glyphs group box
        self._gridGlyphsGroupBox: QGroupBox = QGroupBox(self)
        self._gridGlyphsGroupBox.setTitle('Grid Glyphs')
        self._layout.addWidget(self._gridGlyphsGroupBox)

        # grid glyphs group box layout
        self._gridGlyphsGroupBoxLayout: QGridLayout = QGridLayout(self._gridGlyphsGroupBox)
        self._gridGlyphsGroupBox.setLayout(self._gridGlyphsGroupBoxLayout)

        # point scale label
        self._pointScaleLabel: QLabel = QLabel(self._gridGlyphsGroupBox)
        self._pointScaleLabel.setText('Point Scale:')
        self._gridGlyphsGroupBoxLayout.addWidget(self._pointScaleLabel, 0, 0)

        # point scale box
        self._pointScaleBox: QDoubleSpinBox = QDoubleSpinBox(self._gridGlyphsGroupBox)
        self._pointScaleBox.setDecimals(3)
        self._pointScaleBox.setMinimum(0.001)
        self._pointScaleBox.setMaximum(0.050)
        self._pointScaleBox.setSingleStep(0.001)
        self._gridGlyphsGroupBoxLayout.addWidget(self._pointScaleBox, 0, 1)

        # arrow scale label
        self._arrowScaleLabel: QLabel = QLabel(self._gridGlyphsGroupBox)
        self._arrowScaleLabel.setText('Arrow Scale:')
        self._gridGlyphsGroupBoxLayout.addWidget(self._arrowScaleLabel, 1, 0)

        # arrow scale box
        self._arrowScaleBox: QDoubleSpinBox = QDoubleSpinBox(self._gridGlyphsGroupBox)
        self._arrowScaleBox.setDecimals(3)
        self._arrowScaleBox.setMinimum(0.010)
        self._arrowScaleBox.setMaximum(0.500)
        self._arrowScaleBox.setSingleStep(0.010)
        self._gridGlyphsGroupBoxLayout.addWidget(self._arrowScaleBox, 1, 1)

        # viewport group box
        self._viewportGroupBox: QGroupBox = QGroupBox(self)
        self._viewportGroupBox.setTitle('Viewport')
        self._layout.addWidget(self._viewportGroupBox)

        # viewport group box layout
        self._viewportGroupBoxLayout: QGridLayout = QGridLayout(self._viewportGroupBox)
        self._viewportGroupBox.setLayout(self._viewportGroupBoxLayout)

        # projection label
        self._projectionLabel: QLabel = QLabel(self._viewportGroupBox)
        self._projectionLabel.setText('Projection:')
        self._viewportGroupBoxLayout.addWidget(self._projectionLabel, 0, 0)

        # projection box
        self._projectionBox: QComboBox = QComboBox(self._viewportGroupBox)
        self._projectionBox.addItems(('Perspective', 'Parallel'))
        self._viewportGroupBoxLayout.addWidget(self._projectionBox, 0, 1)

        # lighting label
        self._lightingLabel: QLabel = QLabel(self._viewportGroupBox)
        self._lightingLabel.setText('Lighting:')
        self._viewportGroupBoxLayout.addWidget(self._lightingLabel, 1, 0)

        # lighting box
        self._lightingBox: QComboBox = QComboBox(self._viewportGroupBox)
        self._lightingBox.addItems(('On', 'Off'))
        self._viewportGroupBoxLayout.addWidget(self._lightingBox, 1, 1)

        # font size label
        self._fontSizeLabel: QLabel = QLabel(self._viewportGroupBox)
        self._fontSizeLabel.setText('Font Size:')
        self._viewportGroupBoxLayout.addWidget(self._fontSizeLabel, 2, 0)

        # font size box
        self._fontSizeBox: QSpinBox = QSpinBox(self._viewportGroupBox)
        self._fontSizeBox.setMinimum(5)
        self._fontSizeBox.setMaximum(50)
        self._fontSizeBox.setSingleStep(1)
        self._viewportGroupBoxLayout.addWidget(self._fontSizeBox)

        # background label
        self._backgroundLabel: QLabel = QLabel(self._viewportGroupBox)
        self._backgroundLabel.setText('Background Color:')
        self._viewportGroupBoxLayout.addWidget(self._backgroundLabel, 3, 0)

        # background 1 box
        self._background1Box: QCheckBox = QCheckBox(self._viewportGroupBox)
        self._viewportGroupBoxLayout.addWidget(self._background1Box, 3, 1)

        # background 2 box
        self._background2Box: QCheckBox = QCheckBox(self._viewportGroupBox)
        self._viewportGroupBoxLayout.addWidget(self._background2Box, 4, 1)

        # foreground label
        self._foregroundLabel: QLabel = QLabel(self._viewportGroupBox)
        self._foregroundLabel.setText('Foreground Color:')
        self._viewportGroupBoxLayout.addWidget(self._foregroundLabel, 5, 0)

        # foreground box
        self._foregroundBox: QCheckBox = QCheckBox(self._viewportGroupBox)
        self._viewportGroupBoxLayout.addWidget(self._foregroundBox, 5, 1)
