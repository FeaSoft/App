import sys
import os.path
from process import Subprocess
from application.solverDialog.solverDialogShell import SolverDialogShell
from PySide6.QtWidgets import QWidget, QFileDialog
from PySide6.QtCore import QTimer

class SolverDialog(SolverDialogShell):
    '''
    The solver dialog.
    '''

    # attribute slots
    __slots__ = (
        '_timer', '_solverProcess', '_modelDatabaseFile', '_solverJobInputFile', '_outputDatabaseFile', '_logFile',
        '_runSolverNext'
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        '''Solver dialog constructor.'''
        super().__init__(parent)
        # file paths
        self._modelDatabaseFile:  str | None = None
        self._solverJobInputFile: str | None = None
        self._outputDatabaseFile: str | None = None
        self._logFile:            str | None = None
        # solver process
        self._runSolverNext: bool = False
        self._solverProcess: Subprocess = Subprocess()
        # timer
        self._timer: QTimer = QTimer(self)
        self._timer.timeout.connect(self.onTimerTimeout) # type: ignore
        self._timer.start(250)
        # connections
        self._startSolverButton.clicked.connect(self.onStartSolver)             # type: ignore
        self._terminateSolverButton.clicked.connect(self.onTerminateSolver)     # type: ignore
        self._openModelDatabaseButton.clicked.connect(self.onOpenModelDatabase) # type: ignore

    def onTimerTimeout(self) -> None:
        '''
        This method is executed once every n units of time.
        This method allows the GUI to show the current status of the solver process.
        The log is also updated.
        '''
        # update GUI to show current solver process status and info
        self._statusBox.setText('Alive' if self._solverProcess.isAlive() else 'Dead')
        self._cpuBox.setText(str(self._solverProcess.cpuPercentage()) + '%')
        self._memoryBox.setText(str(self._solverProcess.memory()) + ' MB')
        if self._solverProcess.isAlive(): self._timeBox.setText(str(self._solverProcess.cpuTime()) + ' s')

        # enable/disable action buttons
        self._startSolverButton.setEnabled(not self._solverProcess.isAlive())
        self._terminateSolverButton.setEnabled(self._solverProcess.isAlive())

        # file paths
        self._modelDatabaseBox.setText(self._modelDatabaseFile if self._modelDatabaseFile else '...')
        self._solverJobInputBox.setText(self._solverJobInputFile if self._solverJobInputFile else '...')
        self._outputDatabaseBox.setText(self._outputDatabaseFile if self._outputDatabaseFile else '...')
        self._logFileBox.setText(self._logFile if self._logFile else '...')

        # check if preprocessor is successfully done
        if self._solverProcess.exitCode() == 0:
            # append CPU time to log
            if self._logFile:
                with open(self._logFile, 'a') as file:
                    file.write('Elapsed CPU time: ' + self._timeBox.text() + '\n\n')
            # reset exit code to None
            self._solverProcess.terminate()
            # run solver if requested
            if self._runSolverNext:
                self._timeBox.setText('0 s')
                self.startSolver()

        # update log
        if self._logFile and os.path.isfile(self._logFile):
            with open(self._logFile, 'r') as log:
                logText: str = log.read()
                if logText != self._logBox.toPlainText():
                    self._logBox.setPlainText(logText)
                    self._logBox.verticalScrollBar().setValue(self._logBox.verticalScrollBar().maximum())
        else:
            self._logBox.setPlainText('...')

    def onStartSolver(self) -> None:
        '''On start solver button clicked.'''
        self._startSolverButton.setEnabled(False)
        self.startPreprocessor()

    def onTerminateSolver(self) -> None:
        '''On terminate solver button clicked.'''
        if not self._solverProcess.isAlive():
            raise RuntimeError('the solver process has already been terminated')
        # disable button
        self._terminateSolverButton.setEnabled(False)
        # terminate process
        self._solverProcess.terminate()

    def onOpenModelDatabase(self) -> None:
        '''On open model database button clicked.'''
        filePath: str = QFileDialog.getOpenFileName( # type: ignore
            parent=self,
            caption='Open Database',
            filter='FeaSoft Model Database Files (*.fs_mdb);;All Files (*.*)',
            options=QFileDialog.Option.DontUseNativeDialog
        )[0]
        if filePath != '':
            self._modelDatabaseFile  = os.path.splitext(filePath)[0] + '.fs_mdb'
            self._solverJobInputFile = os.path.splitext(filePath)[0] + '.fs_job'
            self._outputDatabaseFile = os.path.splitext(filePath)[0] + '.fs_odb'
            self._logFile            = os.path.splitext(filePath)[0] + '.fs_log'

    def startPreprocessor(self, preprocessorOnly: bool = False) -> None:
        '''Starts the preprocessor process.'''
        # check for file paths
        if not self._modelDatabaseFile or not self._solverJobInputFile or not self._logFile:
            raise RuntimeError('a model database must first be specified')
        # check for a running process
        if self._solverProcess.isAlive():
            raise RuntimeError('a solver process has already been created')
        # start process
        self._runSolverNext = not preprocessorOnly
        self._solverProcess.start(
            exe=sys.executable,
            args=(
                '-m', 'fs_preprocessor.py', f'"{self._modelDatabaseFile}"', f'"{self._solverJobInputFile}"',
                f'"{self._logFile}"', str(sys.tracebacklimit)
            )
        )

    def startSolver(self) -> None:
        '''Starts the solver process.'''
        # check for file paths
        if not self._outputDatabaseFile or not self._solverJobInputFile or not self._logFile:
            raise RuntimeError('a model database must first be specified')
        # check for a running process
        if self._solverProcess.isAlive():
            raise RuntimeError('a solver process has already been created')
        # start process
        self._runSolverNext = False
        with open(self._logFile, 'a') as log:
            self._solverProcess.start(
                exe='C:/Users/Carlos/Source/Repos/FeaSoft/App/FS_Solver/x64/Release/FS_Solver.exe',
                args=(f'"{self._solverJobInputFile}"', f'"{self._outputDatabaseFile}"'),
                stdout=log,
                stderr=log
            )
