from typing import Any
from visualization import Viewport
from application.optionsResultDialog.optionsResultDialogShell import OptionsResultDialogShell
from PySide6.QtWidgets import QWidget

class OptionsResultDialog(OptionsResultDialogShell):
    '''
    The options > result dialog.
    '''

    # attribute slots
    __slots__ = ()

    def __init__(self, parent: QWidget | None = None) -> None:
        '''Options > result dialog constructor.'''
        super().__init__(parent)
        # initial setup
        self._scaleFactorBox.setText(str(Viewport.deformationScaleFactor()))
        self._showMaxBox.setChecked(Viewport.showMaxPointLabel())
        self._showMinBox.setChecked(Viewport.showMinPointLabel())
        self._customLimitsBox.setChecked(Viewport.useCustomLimits())
        self._maxLimitBox.setText(str(Viewport.customMaxLimit()))
        self._minLimitBox.setText(str(Viewport.customMinLimit()))
        self._maxLimitBox.setEnabled(self._customLimitsBox.isChecked())
        self._minLimitBox.setEnabled(self._customLimitsBox.isChecked())
        self._numberFormatBox.setCurrentText(Viewport.scalarBarNumberFormat())
        self._decimalPlacesBox.setValue(Viewport.scalarBarDecimalPlaces())
        self._colormapBox.setCurrentText(Viewport.colormap().name)
        self._intervalsBox.setValue(Viewport.colormapIntervals())
        self._reverseColormapBox.setChecked(Viewport.reverseColormap())
        # connections
        Viewport.registerCallback(self.onViewportOptionChanged)
        self._scaleFactorBox.editingFinished.connect(self.onScaleFactor)       # type: ignore
        self._showMaxBox.stateChanged.connect(self.onShowMax)                  # type: ignore
        self._showMinBox.stateChanged.connect(self.onShowMin)                  # type: ignore
        self._customLimitsBox.stateChanged.connect(self.onCustomLimits)        # type: ignore
        self._maxLimitBox.editingFinished.connect(self.onMaxLimit)             # type: ignore
        self._minLimitBox.editingFinished.connect(self.onMinLimit)             # type: ignore
        self._numberFormatBox.currentIndexChanged.connect(self.onNumberFormat) # type: ignore
        self._decimalPlacesBox.valueChanged.connect(self.onDecimalPlaces)      # type: ignore
        self._colormapBox.currentIndexChanged.connect(self.onColormap)         # type: ignore
        self._intervalsBox.valueChanged.connect(self.onIntervals)              # type: ignore
        self._reverseColormapBox.stateChanged.connect(self.onReverseColormap)  # type: ignore

    def onViewportOptionChanged(self, optionName: str, optionValue: Any) -> None:
        '''On viewport global option changed.'''
        match optionName:
            case 'DeformationScaleFactor': self._scaleFactorBox.setText(str(optionValue))
            case 'ShowMaxPointLabel': self._showMaxBox.setChecked(optionValue)
            case 'ShowMinPointLabel': self._showMinBox.setChecked(optionValue)
            case 'UseCustomLimits': self._customLimitsBox.setChecked(optionValue)
            case 'CustomMaxLimit': self._maxLimitBox.setText(str(optionValue))
            case 'CustomMinLimit': self._minLimitBox.setText(str(optionValue))
            case 'ScalarBarNumberFormat': self._numberFormatBox.setCurrentText(optionValue)
            case 'ScalarBarDecimalPlaces': self._decimalPlacesBox.setValue(optionValue)
            case 'Colormap': self._colormapBox.setCurrentText(optionValue.name)
            case 'ColormapIntervals': self._intervalsBox.setValue(optionValue)
            case 'ReverseColormap': self._reverseColormapBox.setChecked(optionValue)
            case _: pass

    def onScaleFactor(self) -> None:
        '''On scale factor box editing finished.'''
        try: Viewport.setDeformationScaleFactor(float(self._scaleFactorBox.text()))
        except: self._scaleFactorBox.setText(str(Viewport.deformationScaleFactor()))

    def onShowMax(self) -> None:
        '''On show max box state changed.'''
        Viewport.setShowMaxPointLabel(self._showMaxBox.isChecked())

    def onShowMin(self) -> None:
        '''On show min box state changed.'''
        Viewport.setShowMinPointLabel(self._showMinBox.isChecked())

    def onCustomLimits(self) -> None:
        '''On custom limits box state changed.'''
        self._maxLimitBox.setEnabled(self._customLimitsBox.isChecked())
        self._minLimitBox.setEnabled(self._customLimitsBox.isChecked())
        Viewport.setUseCustomLimits(self._customLimitsBox.isChecked())

    def onMaxLimit(self) -> None:
        '''On max limit box editing finished.'''
        try: Viewport.setCustomMaxLimit(float(self._maxLimitBox.text()))
        except: self._maxLimitBox.setText(str(Viewport.customMaxLimit()))

    def onMinLimit(self) -> None:
        '''On min limit box editing finished.'''
        try: Viewport.setCustomMinLimit(float(self._minLimitBox.text()))
        except: self._minLimitBox.setText(str(Viewport.customMinLimit()))

    def onNumberFormat(self) -> None:
        '''On number format box current index changed.'''
        Viewport.setScalarBarNumberFormat(self._numberFormatBox.currentText()) # type: ignore

    def onDecimalPlaces(self) -> None:
        '''On decimal places box value changed.'''
        Viewport.setScalarBarDecimalPlaces(self._decimalPlacesBox.value())

    def onColormap(self) -> None:
        '''On colormap box current index changed.'''
        Viewport.setColormap(self._colormapBox.currentText())

    def onIntervals(self) -> None:
        '''On intervals box value changed.'''
        Viewport.setColormapIntervals(self._intervalsBox.value())

    def onReverseColormap(self) -> None:
        '''On reverse colormap box state changed.'''
        Viewport.setReverseColormap(self._reverseColormapBox.isChecked())
