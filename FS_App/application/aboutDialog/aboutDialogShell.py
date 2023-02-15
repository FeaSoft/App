from PySide6.QtWidgets import QWidget, QDialog, QVBoxLayout, QLabel
from PySide6.QtGui import Qt, QFont

class AboutDialogShell(QDialog):
    '''
    The help > about dialog shell (basic UI).
    '''

    # attribute slots
    __slots__ = ('_layout', '_title', '_info', '_copyright', '_license', '_repo')

    def __init__(self, parent: QWidget | None = None) -> None:
        '''Help > about dialog shell constructor.'''
        super().__init__(parent)

        # dialog (self)
        self.setWindowTitle('About FeaSoft')
        self.resize(300, 0)

        # layout
        self._layout: QVBoxLayout = QVBoxLayout(self)
        self.setLayout(self._layout)

        # font 0
        font0: QFont = QFont()
        font0.setBold(True)
        font0.setPointSize(14)

        # font 1
        font1: QFont = QFont()
        font1.setBold(True)
        font1.setPointSize(10)

        # title
        self._title: QLabel = QLabel(self)
        self._title.setText('About FeaSoft')
        self._title.setFont(font0)
        self._layout.addWidget(self._title)

        # subtitle
        self._subtitle: QLabel = QLabel(self)
        self._subtitle.setText('Finite element analysis software for solids')
        self._subtitle.setFont(font1)
        self._layout.addWidget(self._subtitle)

        # info
        self._info: QLabel = QLabel(self)
        self._info.setText('fs_app v1.0 | fs_preprocessor v1.0 | fs_solver v1.0')
        self._layout.addWidget(self._info)

        # copyright
        self._copyright: QLabel = QLabel(self)
        self._copyright.setText('© 2023 Carlos Souto. All rights reserved.')
        self._layout.addWidget(self._copyright)

        # license
        self._license: QLabel = QLabel(self)
        self._license.setText('<b>License:</b> <a href="https://www.gnu.org/licenses/gpl-3.0.en.html">GNU General Public License v3.0</a>')
        self._license.setTextFormat(Qt.TextFormat.RichText)
        self._license.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self._license.setOpenExternalLinks(True)
        self._layout.addWidget(self._license)

        # repo
        self._repo: QLabel = QLabel(self)
        self._repo.setText('<b>Repository:</b> <a href="https://github.com/FeaSoft/App">github.com/FeaSoft/App</a>')
        self._repo.setTextFormat(Qt.TextFormat.RichText)
        self._repo.setTextInteractionFlags(Qt.TextInteractionFlag.TextBrowserInteraction)
        self._repo.setOpenExternalLinks(True)
        self._layout.addWidget(self._repo)
