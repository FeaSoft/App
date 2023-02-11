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
        # connections
        Viewport.registerCallback(self.onViewportOptionChanged)
        self._scaleFactorBox.editingFinished.connect(self.onScaleFactor) # type: ignore

    def onViewportOptionChanged(self, optionName: str, optionValue: Any) -> None:
        '''On viewport global option changed.'''
        match optionName:
            case 'DeformationScaleFactor': self._scaleFactorBox.setText(str(optionValue))
            case _: pass

    def onScaleFactor(self) -> None:
        '''On scale factor box editing finished.'''
        try: Viewport.setDeformationScaleFactor(float(self._scaleFactorBox.text()))
        except: self._scaleFactorBox.setText(str(Viewport.deformationScaleFactor()))




        
        
        
        
