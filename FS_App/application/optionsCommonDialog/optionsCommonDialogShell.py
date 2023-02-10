from PySide6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QGridLayout, QGroupBox, QLabel, QCheckBox, QDoubleSpinBox, QComboBox
)

class OptionsCommonDialogShell(QDialog):
    '''
    The options > common dialog shell (basic UI).
    '''

#   # attribute slots
#   __slots__ = (
#       '_layout', '_meshLinesGroupBox', '_meshLinesGroupBoxLayout', '_lineVisibilityLabel', '_lineVisibilityBox',
#       '_lineWidthLabel', '_lineWidthBox', '_lineColorLabel', '_lineColorBox', '_meshCellsGroupBox',
#       '_meshCellsGroupBoxLayout', '_cellRepresentationLabel', '_cellRepresentationBox', '_cellColorLabel',
#       '_cellColorBox', '_meshGlyphsGroupBox', '_meshGlyphsGroupBoxLayout', '_pointScaleLabel', '_pointScaleBox',
#       '_arrowScaleLabel', '_arrowScaleBox'
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

        # mesh lines group box
        self._meshLinesGroupBox: QGroupBox = QGroupBox(self)
        self._meshLinesGroupBox.setTitle('Mesh Lines')
        self._layout.addWidget(self._meshLinesGroupBox)

        # mesh lines group box layout
        self._meshLinesGroupBoxLayout: QGridLayout = QGridLayout(self._meshLinesGroupBox)
        self._meshLinesGroupBox.setLayout(self._meshLinesGroupBoxLayout)

        # line visibility label
        self._lineVisibilityLabel: QLabel = QLabel(self._meshLinesGroupBox)
        self._lineVisibilityLabel.setText('Line Visibility:')
        self._meshLinesGroupBoxLayout.addWidget(self._lineVisibilityLabel, 0, 0)

        # line visibility box
        self._lineVisibilityBox: QCheckBox = QCheckBox(self._meshLinesGroupBox)
        self._meshLinesGroupBoxLayout.addWidget(self._lineVisibilityBox, 0, 1)

        # line width label
        self._lineWidthLabel: QLabel = QLabel(self._meshLinesGroupBox)
        self._lineWidthLabel.setText('Line Width:')
        self._meshLinesGroupBoxLayout.addWidget(self._lineWidthLabel, 1, 0)

        # line width slider
        self._lineWidthBox: QDoubleSpinBox = QDoubleSpinBox(self._meshLinesGroupBox)
        self._lineWidthBox.setDecimals(1)
        self._lineWidthBox.setMinimum(1.0)
        self._lineWidthBox.setMaximum(10.0)
        self._lineWidthBox.setSingleStep(0.5)
        self._meshLinesGroupBoxLayout.addWidget(self._lineWidthBox, 1, 1)

        # line color label
        self._lineColorLabel: QLabel = QLabel(self._meshLinesGroupBox)
        self._lineColorLabel.setText('Line Color:')
        self._meshLinesGroupBoxLayout.addWidget(self._lineColorLabel, 2, 0)

        # line color box
        self._lineColorBox: QCheckBox = QCheckBox(self._meshLinesGroupBox)
        self._lineColorBox.setCheckable(False)
        self._meshLinesGroupBoxLayout.addWidget(self._lineColorBox, 2, 1)

        # mesh cells group box
        self._meshCellsGroupBox: QGroupBox = QGroupBox(self)
        self._meshCellsGroupBox.setTitle('Mesh Cells')
        self._layout.addWidget(self._meshCellsGroupBox)

        # mesh cells group box layout
        self._meshCellsGroupBoxLayout: QGridLayout = QGridLayout(self._meshCellsGroupBox)
        self._meshCellsGroupBox.setLayout(self._meshCellsGroupBoxLayout)

        # cell representation label
        self._cellRepresentationLabel: QLabel = QLabel(self._meshCellsGroupBox)
        self._cellRepresentationLabel.setText('Cell Representation:')
        self._meshCellsGroupBoxLayout.addWidget(self._cellRepresentationLabel, 0, 0)

        # cell representation box
        self._cellRepresentationBox: QComboBox = QComboBox(self._meshCellsGroupBox)
        self._cellRepresentationBox.addItems(('Surface', 'Wireframe'))
        self._meshCellsGroupBoxLayout.addWidget(self._cellRepresentationBox, 0, 1)

        # cell color label
        self._cellColorLabel: QLabel = QLabel(self._meshCellsGroupBox)
        self._cellColorLabel.setText('Cell Color:')
        self._meshCellsGroupBoxLayout.addWidget(self._cellColorLabel, 1, 0)

        # cell color box
        self._cellColorBox: QCheckBox = QCheckBox(self._meshCellsGroupBox)
        self._cellColorBox.setCheckable(False)
        self._meshCellsGroupBoxLayout.addWidget(self._cellColorBox, 1, 1)

        # mesh glyphs group box
        self._meshGlyphsGroupBox: QGroupBox = QGroupBox(self)
        self._meshGlyphsGroupBox.setTitle('Mesh Glyphs')
        self._layout.addWidget(self._meshGlyphsGroupBox)

        # mesh glyphs group box layout
        self._meshGlyphsGroupBoxLayout: QGridLayout = QGridLayout(self._meshGlyphsGroupBox)
        self._meshGlyphsGroupBox.setLayout(self._meshGlyphsGroupBoxLayout)

        # point scale label
        self._pointScaleLabel: QLabel = QLabel(self._meshGlyphsGroupBox)
        self._pointScaleLabel.setText('Point Scale:')
        self._meshGlyphsGroupBoxLayout.addWidget(self._pointScaleLabel, 0, 0)

        # point scale box
        self._pointScaleBox: QDoubleSpinBox = QDoubleSpinBox(self._meshGlyphsGroupBox)
        self._pointScaleBox.setDecimals(3)
        self._pointScaleBox.setMinimum(0.0)
        self._pointScaleBox.setMaximum(100.0)
        self._pointScaleBox.setSingleStep(0.005)
        self._meshGlyphsGroupBoxLayout.addWidget(self._pointScaleBox, 0, 1)

        # arrow scale label
        self._arrowScaleLabel: QLabel = QLabel(self._meshGlyphsGroupBox)
        self._arrowScaleLabel.setText('Arrow Scale:')
        self._meshGlyphsGroupBoxLayout.addWidget(self._arrowScaleLabel, 1, 0)

        # arrow scale box
        self._arrowScaleBox: QDoubleSpinBox = QDoubleSpinBox(self._meshGlyphsGroupBox)
        self._arrowScaleBox.setDecimals(3)
        self._arrowScaleBox.setMinimum(0.0)
        self._arrowScaleBox.setMaximum(100.0)
        self._arrowScaleBox.setSingleStep(0.005)
        self._meshGlyphsGroupBoxLayout.addWidget(self._arrowScaleBox, 1, 1)
