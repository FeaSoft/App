import sys
import os.path
import preprocessor
from multiprocessing import Process
from psutil import Process as ProcessInfo, cpu_count
from application.solverDialog.solverDialogShell import SolverDialogShell
from PySide6.QtWidgets import QWidget, QFileDialog
from PySide6.QtCore import QTimer

class SolverDialog(SolverDialogShell):
    '''
    The solver dialog.
    '''

    # attribute slots
    __slots__ = (
        '_timer', '_solverProcess', '_solverProcessInfo', '_modelDatabaseFile', '_solverJobInputFile',
        '_outputDatabaseFile', '_logFile'
    )

    def __init__(self, parent: QWidget | None = None) -> None:
        '''Solver dialog constructor.'''
        super().__init__(parent)
        # model database file
        self._modelDatabaseFile:  str | None = None
        self._solverJobInputFile: str | None = None
        self._outputDatabaseFile: str | None = None
        self._logFile:            str | None = None
        # timer
        self._timer: QTimer = QTimer(self)
        self._timer.timeout.connect(self.onTimerTimeOut) # type: ignore
        self._timer.start(250)
        # solver process and process info
        self._solverProcess: Process | None = None
        self._solverProcessInfo: ProcessInfo | None = None
        # connections
        self._startSolverButton.clicked.connect(self.onStartSolver)             # type: ignore
        self._terminateSolverButton.clicked.connect(self.onTerminateSolver)     # type: ignore
        self._openModelDatabaseButton.clicked.connect(self.onOpenModelDatabase) # type: ignore

    def onTimerTimeOut(self) -> None:
        '''
        This method is executed once every n units of time.
        This method allows the GUI to show the current status of the solver process.
        The log is also updated.
        '''
        try:
            # clean process resources if it has finished
            if self._solverProcess and not self._solverProcess.is_alive():
                self._solverProcess.close()
                self._solverProcess = None
                self._solverProcessInfo = None

            # process status and info
            if self._solverProcess and self._solverProcessInfo and self._solverProcess.is_alive():
                # compute CPU percentage, times, and memory usage
                cpuPercentage: int = round(self._solverProcessInfo.cpu_percent()/cpu_count())
                cpuUserTime: float = self._solverProcessInfo.cpu_times().user
                cpuSystemTime: float = self._solverProcessInfo.cpu_times().system
                cpuTime: float = round(cpuUserTime + cpuSystemTime, 3)
                memory: int = round(self._solverProcessInfo.memory_info().rss * 1e-6)
                # display computed values
                self._statusBox.setText('Alive')
                self._cpuBox.setText(str(cpuPercentage) + '%')
                self._timeBox.setText(str(cpuTime) + ' s')
                self._memoryBox.setText(str(memory) + ' MB')
                # cpu box color
                if        cpuPercentage <= 0: self._cpuBox.setStyleSheet('background: white;')
                elif  0 < cpuPercentage < 25: self._cpuBox.setStyleSheet('background: rgb(0,255,0);')
                elif 25 < cpuPercentage < 50: self._cpuBox.setStyleSheet('background: rgb(255,255,0);')
                elif 50 < cpuPercentage < 75: self._cpuBox.setStyleSheet('background: rgb(255,127,0);')
                else:                         self._cpuBox.setStyleSheet('background: rgb(255,0,0);')
            else:
                self._cpuBox.setStyleSheet('background: white;')
                self._statusBox.setText('Dead')
                self._cpuBox.setText('0%')
                self._memoryBox.setText('0 MB')

            # enable or disable UI elements
            self._startSolverButton.setEnabled(bool(not self._solverProcess))
            self._terminateSolverButton.setEnabled(bool(self._solverProcess and self._solverProcess.is_alive()))

            # file paths
            if self._modelDatabaseFile and self._solverJobInputFile and self._outputDatabaseFile and self._logFile:
                self._modelDatabaseBox.setText(self._modelDatabaseFile)
                self._solverJobInputBox.setText(self._solverJobInputFile)
                self._outputDatabaseBox.setText(self._outputDatabaseFile)
                self._logFileBox.setText(self._logFile)
            else:
                self._modelDatabaseBox.setText('...')
                self._solverJobInputBox.setText('...')
                self._outputDatabaseBox.setText('...')
                self._logFileBox.setText('...')

            # update log
            if self._logFile and os.path.isfile(self._logFile):
                with open(self._logFile, 'r') as log:
                    logText: str = log.read()
                    if logText != self._logBox.toPlainText():
                        self._logBox.setText(logText)
            else:
                self._logBox.setText('...')

        except:
            # process may have died during info lookup (not really a problem)
            pass

    def onStartSolver(self) -> None:
        '''On start solver button clicked.'''
        # check for model database
        if not self._modelDatabaseFile:
            raise RuntimeError('a model database must first be opened')
        # check if a process currently exists
        if self._solverProcess or self._solverProcessInfo:
            raise RuntimeError('a solver process has already been created')
        # disable button
        self._startSolverButton.setEnabled(False)
        # create and start solver process
        self._solverProcess = Process(
            target=preprocessor.start,
            args=(
                self._modelDatabaseFile, self._solverJobInputFile, self._outputDatabaseFile, self._logFile,
                sys.tracebacklimit
            )
        )
        self._solverProcess.start()
        # create process info object
        self._solverProcessInfo = ProcessInfo(self._solverProcess.pid)

    def onTerminateSolver(self) -> None:
        '''On terminate solver button clicked.'''
        # check if a process currently exists
        if not self._solverProcess or not self._solverProcess.is_alive():
            raise RuntimeError('the solver process has already been terminated')
        # disable button
        self._terminateSolverButton.setEnabled(False)
        # terminate process
        self._solverProcess.terminate()
        self._solverProcess.join()
        self._solverProcess.close()
        self._solverProcess = None
        self._solverProcessInfo = None

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
