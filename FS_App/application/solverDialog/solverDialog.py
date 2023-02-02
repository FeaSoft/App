from typing import Literal

from multiprocessing import Process



from application.solverDialog.solverDialogShell import SolverDialogShell
from PySide6.QtWidgets import QWidget
from PySide6.QtCore import QTimer






def function() -> None:
    import time
    for i in range(5):
        print(i)
        time.sleep(2)

class SolverDialog(SolverDialogShell):
    

    # attribute slots
    __slots__ = ('_timer', '_solverProcess', '_solveProcessStatus')

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._timer: QTimer = QTimer(self)
        self._timer.timeout.connect(self.onTimeOut) # type: ignore
        self._timer.start(250)

        self._solverProcess: Process | None = None
        self._solveProcessStatus: Literal['Dead', 'Alive'] = 'Dead'

        self._startSolverButton.clicked.connect(self.onStartSolver) # type: ignore
        self._terminateSolverButton.clicked.connect(self.onTerminateSolver) # type: ignore


    def onTimeOut(self) -> None:
        if self._solverProcess and not self._solverProcess.is_alive():
            self._solverProcess.close()
            self._solverProcess = None
            self._solveProcessStatus = 'Dead'
            
        
        print(self._solveProcessStatus)


    def onStartSolver(self) -> None:
        if self._solverProcess or self._solveProcessStatus == 'Alive':
            raise RuntimeError('...')


        self._solveProcessStatus = 'Alive'
        self._solverProcess = Process(target=function)
        self._solverProcess.start()
        
    def onTerminateSolver(self) -> None:
        if not self._solverProcess: return

        self._solverProcess.terminate()
        self._solverProcess.join()
        print('joined')
        self._solverProcess.close()
        self._solverProcess = None
        self._solveProcessStatus = 'Dead'




# from multiprocessing import Process

# process: Process = Process(target=function)

# def start():
#     process.start()
    
    
#     # process.join()

# def kill():
#     if process.is_alive(): process.terminate()
#     while process.is_alive(): print('miau')
#     process.close()
#     print('dieded')

    
    



# from PySide6.QtWidgets import QWidget, QPushButton, QVBoxLayout


# class SolverInterfaceShell(QWidget):

#     __slots__ = ('_layout', '_button1', '_button2')

#     def __init__(self, parent: QWidget | None = None) -> None:
#         super().__init__(parent)

#         self._layout: QVBoxLayout = QVBoxLayout(self)
#         self.setLayout(self._layout)

#         self._button1: QPushButton = QPushButton(self)
#         self._layout.addWidget(self._button1)

#         self._button2: QPushButton = QPushButton(self)
#         self._layout.addWidget(self._button2)

#         self._button1.clicked.connect(start)
#         self._button2.clicked.connect(kill)


# if __name__ == '__main__':
#     from PySide6.QtWidgets import QApplication

#     app = QApplication()
#     main = SolverInterfaceShell()
#     main.show()
#     app.exec()
        