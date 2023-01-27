import sys
from dataModel import ModelDatabase
from PySide6.QtWidgets import QApplication

from application import MainWindow



mdb = ModelDatabase()

app = QApplication()
app.setStyle('Fusion')

mainWindow = MainWindow()
mainWindow.show()



mainWindow._modelTree.setModelDatabase(mdb)


sys.tracebacklimit = 0
sys.stdout = mainWindow.terminal.stdout
sys.stderr = mainWindow.terminal.stderr
sys.stdin = mainWindow.terminal.stdin


mdb.materials.new()
mdb.materials.new()
mdb.materials.new()

mdb.sections.new()
mdb.sections.new()
mdb.sections.new()

app.exec()

print('ok')
