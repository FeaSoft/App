from dataModel import ModelDatabase
from control import ModelDatabaseControl
from PySide6.QtWidgets import QApplication

mdb = ModelDatabase()

app = QApplication()
app.setStyle('Fusion')

control = ModelDatabaseControl(None, mdb)
control.show()

mdb.materials.new()
mdb.materials.new()
mdb.materials.new()

mdb.sections.new()
mdb.sections.new()
mdb.sections.new()

app.exec()
