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
        # connections
        Viewport.registerCallback(self.onViewportOptionChanged)
        self._scaleFactorBox.editingFinished.connect(self.onScaleFactor) # type: ignore
        self._showMaxBox.stateChanged.connect(self.onShowMax)            # type: ignore
        self._showMinBox.stateChanged.connect(self.onShowMin)            # type: ignore

    def onViewportOptionChanged(self, optionName: str, optionValue: Any) -> None:
        '''On viewport global option changed.'''
        match optionName:
            case 'DeformationScaleFactor': self._scaleFactorBox.setText(str(optionValue))
            case 'ShowMaxPointLabel': self._showMaxBox.setChecked(optionValue)
            case 'ShowMinPointLabel': self._showMinBox.setChecked(optionValue)
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
