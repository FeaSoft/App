




from application.solverDialog.solverDialogShell import SolverDialogShell



class SolverDialog(SolverDialogShell):
    pass




# import time



# from multiprocessing import Process


# def function():
#     for i in range(10):
#         print(i)
#         time.sleep(2)

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
        