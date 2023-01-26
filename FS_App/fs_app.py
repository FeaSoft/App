import sys
from dataModel import ModelDatabase
from PySide6.QtWidgets import QApplication

from application.mainWindow.mainWindowShell import MainWindowShell

mdb = ModelDatabase()

app = QApplication()
app.setStyle('Fusion')

mainWindow = MainWindowShell()
mainWindow.show()

mainWindow._modelTree.setModelDatabase(mdb)


sys.tracebacklimit = 0
sys.stdout = mainWindow._terminal.stdout
sys.stderr = mainWindow._terminal.stderr
sys.stdin = mainWindow._terminal.stdin


mdb.materials.new()
mdb.materials.new()
mdb.materials.new()

mdb.sections.new()
mdb.sections.new()
mdb.sections.new()

app.exec()
