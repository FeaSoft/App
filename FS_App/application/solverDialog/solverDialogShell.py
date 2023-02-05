from PySide6.QtGui import Qt, QIcon
from PySide6.QtWidgets import (
    QWidget, QDialog, QGridLayout, QHBoxLayout, QVBoxLayout, QGroupBox, QLabel, QLineEdit, QRadioButton, QFrame, QSizePolicy,
    QPushButton, QPlainTextEdit
)

class SolverDialogShell(QDialog):
    '''
    The solver dialog shell (basic UI).
    '''

    # attribute slots (not allowed, QT crashes)
    # __slots__ = ...

    def __init__(self, parent: QWidget | None = None) -> None:
        '''Solver dialog shell constructor.'''
        super().__init__(parent)

        # widget (self)
        self.setWindowTitle('Solver Dialog')
        self.resize(480, 720)

        # layout
        self._layout: QGridLayout = QGridLayout(self)
        self.setLayout(self._layout)

        # current job group box
        self._currentJobGroupBox: QGroupBox = QGroupBox(self)
        self._currentJobGroupBox.setTitle('Current Job')
        self._layout.addWidget(self._currentJobGroupBox, 0, 0, 1, 2)

        # current job group box layout
        self._currentJobGroupBoxLayout: QGridLayout = QGridLayout(self._currentJobGroupBox)
        self._currentJobGroupBox.setLayout(self._currentJobGroupBoxLayout)

        # model database label
        self._modelDatabaseLabel: QLabel = QLabel(self._currentJobGroupBox)
        self._modelDatabaseLabel.setText('Model Database:')
        self._modelDatabaseLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._currentJobGroupBoxLayout.addWidget(self._modelDatabaseLabel, 0, 0)

        # model database box
        self._modelDatabaseBox: QLineEdit = QLineEdit(self._currentJobGroupBox)
        self._modelDatabaseBox.setReadOnly(True)
        self._modelDatabaseBox.setText('...')
        self._currentJobGroupBoxLayout.addWidget(self._modelDatabaseBox, 0, 1)

        # open model database button
        self._openModelDatabaseButton: QPushButton = QPushButton(self._currentJobGroupBox)
        self._openModelDatabaseButton.setIcon(QIcon('./resources/images/file-open.svg'))
        self._currentJobGroupBoxLayout.addWidget(self._openModelDatabaseButton, 0, 2)

        # solver job input label
        self._solverJobInputLabel: QLabel = QLabel(self._currentJobGroupBox)
        self._solverJobInputLabel.setText('Solver Job Input:')
        self._solverJobInputLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._currentJobGroupBoxLayout.addWidget(self._solverJobInputLabel, 1, 0)

        # solver job input box
        self._solverJobInputBox: QLineEdit = QLineEdit(self._currentJobGroupBox)
        self._solverJobInputBox.setReadOnly(True)
        self._solverJobInputBox.setText('...')
        self._currentJobGroupBoxLayout.addWidget(self._solverJobInputBox, 1, 1)

        # output database label
        self._outputDatabaseLabel: QLabel = QLabel(self._currentJobGroupBox)
        self._outputDatabaseLabel.setText('Output Database:')
        self._outputDatabaseLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._currentJobGroupBoxLayout.addWidget(self._outputDatabaseLabel, 2, 0)

        # output database box
        self._outputDatabaseBox: QLineEdit = QLineEdit(self._currentJobGroupBox)
        self._outputDatabaseBox.setReadOnly(True)
        self._outputDatabaseBox.setText('...')
        self._currentJobGroupBoxLayout.addWidget(self._outputDatabaseBox, 2, 1)

        # log file label
        self._logFileLabel: QLabel = QLabel(self._currentJobGroupBox)
        self._logFileLabel.setText('Log File:')
        self._logFileLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._currentJobGroupBoxLayout.addWidget(self._logFileLabel, 3, 0)

        # log file box
        self._logFileBox: QLineEdit = QLineEdit(self._currentJobGroupBox)
        self._logFileBox.setReadOnly(True)
        self._logFileBox.setText('...')
        self._currentJobGroupBoxLayout.addWidget(self._logFileBox, 3, 1)

        # analysis type group box
        self._analysisTypeGroupBox: QGroupBox = QGroupBox(self)
        self._analysisTypeGroupBox.setTitle('Analysis Type')
        self._layout.addWidget(self._analysisTypeGroupBox, 1, 0, 1, 2)

        # analysis type group box layout
        self._analysisTypeGroupBoxLayout: QGridLayout = QGridLayout(self._analysisTypeGroupBox)
        self._analysisTypeGroupBox.setLayout(self._analysisTypeGroupBoxLayout)

        # size policy
        sizePolicy0: QSizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy0.setHorizontalStretch(5)

        # static button
        self._staticButton: QRadioButton = QRadioButton(self._analysisTypeGroupBox)
        self._staticButton.setText('Static')
        self._staticButton.setChecked(True)
        self._staticButton.setSizePolicy(sizePolicy0)
        self._analysisTypeGroupBoxLayout.addWidget(self._staticButton, 0, 0)

        # frequency button
        self._frequencyButton: QRadioButton = QRadioButton(self._analysisTypeGroupBox)
        self._frequencyButton.setText('Frequency')
        self._frequencyButton.setSizePolicy(sizePolicy0)
        self._analysisTypeGroupBoxLayout.addWidget(self._frequencyButton, 1, 0)

        # buckle button
        self._buckleButton: QRadioButton = QRadioButton(self._analysisTypeGroupBox)
        self._buckleButton.setText('Buckle')
        self._buckleButton.setSizePolicy(sizePolicy0)
        self._analysisTypeGroupBoxLayout.addWidget(self._buckleButton, 2, 0)

        # eigenvalues group box
        self._eigenvaluesGroupBox: QGroupBox = QGroupBox(self._analysisTypeGroupBox)
        self._eigenvaluesGroupBox.setTitle('Number of Eigenvalues')
        self._analysisTypeGroupBoxLayout.addWidget(self._eigenvaluesGroupBox, 0, 1, 3, 1)

        # eigenvalues group box layout
        self._eigenvaluesGroupBoxLayout: QHBoxLayout = QHBoxLayout(self._eigenvaluesGroupBox)
        self._eigenvaluesGroupBox.setLayout(self._eigenvaluesGroupBoxLayout)

        # eigenvalues label
        self._eigenvaluesLabel: QLabel = QLabel(self._eigenvaluesGroupBox)
        self._eigenvaluesLabel.setText('Value:')
        self._eigenvaluesGroupBoxLayout.addWidget(self._eigenvaluesLabel)

        # eigenvalues box
        self._eigenvaluesBox: QLineEdit = QLineEdit(self._eigenvaluesGroupBox)
        self._eigenvaluesBox.setFixedWidth(120)
        self._eigenvaluesGroupBoxLayout.addWidget(self._eigenvaluesBox)

        # size policy
        sizePolicy1: QSizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(3)

        # space
        self._space: QFrame = QFrame(self._analysisTypeGroupBox)
        self._space.setSizePolicy(sizePolicy1)
        self._analysisTypeGroupBoxLayout.addWidget(self._space, 0, 2, 3, 1)

        # size policy
        sizePolicy2: QSizePolicy = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy2.setHorizontalStretch(1)

        # process group box
        self._processGroupBox: QGroupBox = QGroupBox(self)
        self._processGroupBox.setTitle('Solver Process')
        self._processGroupBox.setSizePolicy(sizePolicy2)
        self._layout.addWidget(self._processGroupBox, 2, 0, 1 ,1)

        # process group box layout
        self._processGroupBoxLayout: QGridLayout = QGridLayout(self._processGroupBox)
        self._processGroupBox.setLayout(self._processGroupBoxLayout)

        # status label
        self._statusLabel: QLabel = QLabel(self._processGroupBox)
        self._statusLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._statusLabel.setText('Process Status:')
        self._processGroupBoxLayout.addWidget(self._statusLabel, 0, 0)

        # status box
        self._statusBox: QLineEdit = QLineEdit(self._processGroupBox)
        self._statusBox.setReadOnly(True)
        self._statusBox.setText('Dead')
        self._processGroupBoxLayout.addWidget(self._statusBox, 0, 1)

        # cpu label
        self._cpuLabel: QLabel = QLabel(self._processGroupBox)
        self._cpuLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._cpuLabel.setText('CPU Usage:')
        self._processGroupBoxLayout.addWidget(self._cpuLabel, 1, 0)

        # cpu box
        self._cpuBox: QLineEdit = QLineEdit(self._processGroupBox)
        self._cpuBox.setReadOnly(True)
        self._cpuBox.setText('0%')
        self._processGroupBoxLayout.addWidget(self._cpuBox, 1, 1)

        # time label
        self._timeLabel: QLabel = QLabel(self._processGroupBox)
        self._timeLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._timeLabel.setText('CPU Time:')
        self._processGroupBoxLayout.addWidget(self._timeLabel, 2, 0)

        # time box
        self._timeBox: QLineEdit = QLineEdit(self._processGroupBox)
        self._timeBox.setReadOnly(True)
        self._timeBox.setText('0 s')
        self._processGroupBoxLayout.addWidget(self._timeBox, 2, 1)

        # memory label
        self._memoryLabel: QLabel = QLabel(self._processGroupBox)
        self._memoryLabel.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        self._memoryLabel.setText('Memory:')
        self._processGroupBoxLayout.addWidget(self._memoryLabel, 3, 0)

        # memory box
        self._memoryBox: QLineEdit = QLineEdit(self._processGroupBox)
        self._memoryBox.setReadOnly(True)
        self._memoryBox.setText('0 MB')
        self._processGroupBoxLayout.addWidget(self._memoryBox, 3, 1)

        # actions group box
        self._actionsGroupBox: QGroupBox = QGroupBox(self)
        self._actionsGroupBox.setTitle('Actions')
        self._actionsGroupBox.setSizePolicy(sizePolicy2)
        self._layout.addWidget(self._actionsGroupBox, 2, 1, 1, 1)

        # actions group box layout
        self._actionsGroupBoxLayout: QVBoxLayout = QVBoxLayout(self._actionsGroupBox)
        self._actionsGroupBox.setLayout(self._actionsGroupBoxLayout)

        # start solver button
        self._startSolverButton: QPushButton = QPushButton(self._actionsGroupBox)
        self._startSolverButton.setEnabled(False)
        self._startSolverButton.setText('Start Solver Process')
        self._actionsGroupBoxLayout.addWidget(self._startSolverButton)

        # terminate solver button
        self._terminateSolverButton: QPushButton = QPushButton(self._actionsGroupBox)
        self._terminateSolverButton.setEnabled(False)
        self._terminateSolverButton.setText('Terminate Solver Process')
        self._actionsGroupBoxLayout.addWidget(self._terminateSolverButton)

        # write solver job input button
        self._writeSolverJobInputButton: QPushButton = QPushButton(self._actionsGroupBox)
        self._writeSolverJobInputButton.setEnabled(False)
        self._writeSolverJobInputButton.setText('Write Solver Job Input')
        self._actionsGroupBoxLayout.addWidget(self._writeSolverJobInputButton)

        # open output database button
        self._openOutputDatabaseButton: QPushButton = QPushButton(self._actionsGroupBox)
        self._openOutputDatabaseButton.setEnabled(False)
        self._openOutputDatabaseButton.setText('Open Output Database')
        self._actionsGroupBoxLayout.addWidget(self._openOutputDatabaseButton)

        # log frame
        self._logFrame: QFrame = QFrame(self)
        self._layout.addWidget(self._logFrame, 3, 0, 1, 2)

        # log frame layout
        self._logFrameLayout: QVBoxLayout = QVBoxLayout(self._logFrame)
        self._logFrameLayout.setContentsMargins(0, 0, 0, 0)
        self._logFrame.setLayout(self._logFrameLayout)

        # log label
        self._logLabel: QLabel = QLabel(self._logFrame)
        self._logLabel.setText('Log')
        self._logFrameLayout.addWidget(self._logLabel)

        # log box
        self._logBox: QPlainTextEdit = QPlainTextEdit(self._logFrame)
        self._logBox.setReadOnly(True)
        self._logBox.setPlainText('...')
        self._logFrameLayout.addWidget(self._logBox)
