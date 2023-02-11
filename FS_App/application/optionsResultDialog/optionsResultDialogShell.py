from visualization import Colormaps
from PySide6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QGridLayout, QGroupBox, QLabel, QLineEdit, QCheckBox, QSizePolicy, QComboBox,
    QSpinBox
)

class OptionsResultDialogShell(QDialog):
    '''
    The options > result dialog shell (basic UI).
    '''

#   # attribute slots (crashes QT)
#   __slots__ = (
#       '_layout', '_deformationGroupBox', '_deformationGroupBoxLayout', '_scaleFactorLabel', '_scaleFactorBox',
#       '_limitsGroupBox', '_limitsGroupBoxLayout', '_showMaxLabel', '_showMaxBox', '_showMinLabel', '_showMinBox',
#       '_customLimitsLabel', '_customLimitsBox', '_maxLimitLabel', '_maxLimitBox', '_minLimitLabel', '_minLimitBox',
#       '_scalarBarGroupBox', '_scalarBarGroupBoxLayout', '_numberFormatLabel', '_numberFormatBox',
#       '_decimalPlacesLabel', '_decimalPlacesBox', '_colormapLabel', '_colormapBox', '_intervalsLabel',
#       '_intervalsBox', '_reverseColormapLabel', '_reverseColormapBox'
#   )

    def __init__(self, parent: QWidget | None = None) -> None:
        '''Options > result dialog shell constructor.'''
        super().__init__(parent)

        # dialog (self)
        self.setWindowTitle('Result Options')
        self.resize(300, 0)

        # layout
        self._layout: QVBoxLayout = QVBoxLayout(self)
        self.setLayout(self._layout)

        # deformation group box
        self._deformationGroupBox: QGroupBox = QGroupBox(self)
        self._deformationGroupBox.setTitle('Deformation')
        self._layout.addWidget(self._deformationGroupBox)

        # deformation group box layout
        self._deformationGroupBoxLayout: QGridLayout = QGridLayout(self._deformationGroupBox)
        self._deformationGroupBox.setLayout(self._deformationGroupBoxLayout)

        # scale factor label
        self._scaleFactorLabel: QLabel = QLabel(self._deformationGroupBox)
        self._scaleFactorLabel.setText('Scale Factor:')
        self._deformationGroupBoxLayout.addWidget(self._scaleFactorLabel, 0, 0)

        # scale factor box
        self._scaleFactorBox: QLineEdit = QLineEdit(self._deformationGroupBox)
        self._scaleFactorBox.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        self._deformationGroupBoxLayout.addWidget(self._scaleFactorBox, 0, 1)

        # limits group box
        self._limitsGroupBox: QGroupBox = QGroupBox(self)
        self._limitsGroupBox.setTitle('Limits')
        self._layout.addWidget(self._limitsGroupBox)

        # limits group box layout
        self._limitsGroupBoxLayout: QGridLayout = QGridLayout(self._limitsGroupBox)
        self._limitsGroupBox.setLayout(self._limitsGroupBoxLayout)

        # show max label
        self._showMaxLabel: QLabel = QLabel(self._limitsGroupBox)
        self._showMaxLabel.setText('Show Max. Location:')
        self._limitsGroupBoxLayout.addWidget(self._showMaxLabel, 0, 0)

        # show max box
        self._showMaxBox: QCheckBox = QCheckBox(self._limitsGroupBox)
        self._limitsGroupBoxLayout.addWidget(self._showMaxBox, 0, 1)

        # show min label
        self._showMinLabel: QLabel = QLabel(self._limitsGroupBox)
        self._showMinLabel.setText('Show Min. Location:')
        self._limitsGroupBoxLayout.addWidget(self._showMinLabel, 1, 0)

        # show min box
        self._showMinBox: QCheckBox = QCheckBox(self._limitsGroupBox)
        self._limitsGroupBoxLayout.addWidget(self._showMinBox, 1, 1)

        # custom limits label
        self._customLimitsLabel: QLabel = QLabel(self._limitsGroupBox)
        self._customLimitsLabel.setText('Use Custom Limits:')
        self._limitsGroupBoxLayout.addWidget(self._customLimitsLabel, 2, 0)

        # custom limits box
        self._customLimitsBox: QCheckBox = QCheckBox(self._limitsGroupBox)
        self._limitsGroupBoxLayout.addWidget(self._customLimitsBox, 2, 1)

        # max limit label
        self._maxLimitLabel: QLabel = QLabel(self._limitsGroupBox)
        self._maxLimitLabel.setText('Max. Limit:')
        self._limitsGroupBoxLayout.addWidget(self._maxLimitLabel, 3, 0)

        # max limit box
        self._maxLimitBox: QLineEdit = QLineEdit(self._limitsGroupBox)
        self._maxLimitBox.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        self._limitsGroupBoxLayout.addWidget(self._maxLimitBox, 3, 1)

        # min limit label
        self._minLimitLabel: QLabel = QLabel(self._limitsGroupBox)
        self._minLimitLabel.setText('Min. Limit:')
        self._limitsGroupBoxLayout.addWidget(self._minLimitLabel, 4, 0)

        # min limit box
        self._minLimitBox: QLineEdit = QLineEdit(self._limitsGroupBox)
        self._minLimitBox.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))
        self._limitsGroupBoxLayout.addWidget(self._minLimitBox, 4, 1)

        # scalar bar group box
        self._scalarBarGroupBox: QGroupBox = QGroupBox(self)
        self._scalarBarGroupBox.setTitle('Scalar Bar')
        self._layout.addWidget(self._scalarBarGroupBox)

        # scalar bar group box layout
        self._scalarBarGroupBoxLayout: QGridLayout = QGridLayout(self._scalarBarGroupBox)
        self._scalarBarGroupBox.setLayout(self._scalarBarGroupBoxLayout)

        # number format label
        self._numberFormatLabel: QLabel = QLabel(self._scalarBarGroupBox)
        self._numberFormatLabel.setText('Number Format:')
        self._scalarBarGroupBoxLayout.addWidget(self._numberFormatLabel, 0, 0)

        # number format box
        self._numberFormatBox: QComboBox = QComboBox(self._scalarBarGroupBox)
        self._numberFormatBox.addItems(('Scientific', 'Fixed'))
        self._scalarBarGroupBoxLayout.addWidget(self._numberFormatBox, 0, 1)

        # decimal places label
        self._decimalPlacesLabel: QLabel = QLabel(self._scalarBarGroupBox)
        self._decimalPlacesLabel.setText('Decimal Places:')
        self._scalarBarGroupBoxLayout.addWidget(self._decimalPlacesLabel, 1, 0)

        # decimal places box
        self._decimalPlacesBox: QSpinBox = QSpinBox(self._scalarBarGroupBox)
        self._decimalPlacesBox.setMinimum(0)
        self._decimalPlacesBox.setMaximum(9)
        self._decimalPlacesBox.setSingleStep(1)
        self._scalarBarGroupBoxLayout.addWidget(self._decimalPlacesBox, 1, 1)

        # colormap label
        self._colormapLabel: QLabel = QLabel(self._scalarBarGroupBox)
        self._colormapLabel.setText('Colormap:')
        self._scalarBarGroupBoxLayout.addWidget(self._colormapLabel, 2, 0)

        # colormap box
        self._colormapBox: QComboBox = QComboBox(self._scalarBarGroupBox)
        self._colormapBox.addItems(tuple(x.name for x in Colormaps))
        self._scalarBarGroupBoxLayout.addWidget(self._colormapBox, 2, 1)

        # intervals label
        self._intervalsLabel: QLabel = QLabel(self._scalarBarGroupBox)
        self._intervalsLabel.setText('Intervals:')
        self._scalarBarGroupBoxLayout.addWidget(self._intervalsLabel, 3, 0)

        # intervals box
        self._intervalsBox: QSpinBox = QSpinBox(self._scalarBarGroupBox)
        self._intervalsBox.setMinimum(2)
        self._intervalsBox.setMaximum(64)
        self._intervalsBox.setSingleStep(1)
        self._scalarBarGroupBoxLayout.addWidget(self._intervalsBox, 3, 1)

        # reverse colormap label
        self._reverseColormapLabel: QLabel = QLabel(self._scalarBarGroupBox)
        self._reverseColormapLabel.setText('Reverse Colormap:')
        self._scalarBarGroupBoxLayout.addWidget(self._reverseColormapLabel, 4, 0)

        # reverse colormap box
        self._reverseColormapBox: QCheckBox = QCheckBox(self._scalarBarGroupBox)
        self._scalarBarGroupBoxLayout.addWidget(self._reverseColormapBox, 4, 1)
