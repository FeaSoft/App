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
