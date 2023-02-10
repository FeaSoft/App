from typing import Any
from visualization import Viewport
from application.optionsCommonDialog.optionsCommonDialogShell import OptionsCommonDialogShell
from PySide6.QtWidgets import QWidget

class OptionsCommonDialog(OptionsCommonDialogShell):
    '''
    The options > common dialog.
    '''

    # attribute slots
    __slots__ = ()

    def __init__(self, parent: QWidget | None = None) -> None:
        '''Options > common dialog constructor.'''
        super().__init__(parent)
        # unfortunate initial setup
        self._lineVisibilityBox.setChecked(Viewport.lineVisibility())
        # setup connections
        Viewport.registerCallback(self.onViewportOptionChanged)
        self._lineVisibilityBox.stateChanged.connect(self.onLineVisibilityBox) # type: ignore

    def onViewportOptionChanged(self, optionName: str, optionValue: Any) -> None:
        '''On viewport global option changed.'''
        match optionName:
            case 'LineVisibility': self._lineVisibilityBox.setChecked(optionValue)
            case _: pass

    def onLineVisibilityBox(self) -> None:
        '''On line visibility box state changed.'''
        Viewport.setLineVisibility(self._lineVisibilityBox.isChecked())
        












