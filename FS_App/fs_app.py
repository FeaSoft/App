# https://gitlab.kitware.com/vtk/vtk/-/issues/18800
# updates: mainWindow.py & viewport.py & meshRenderObject.py




if __name__ == '__main__':

    import sys
    import application as app

    # sys.tracebacklimit = 0
    sys.stdout = app.current.mainWindow.terminal.stdout
    sys.stderr = app.current.mainWindow.terminal.stderr
    sys.stdin  = app.current.mainWindow.terminal.stdin

    # start the application event loop
    sys.exit(app.current.start())


# from application import current as app; app.mainWindow.viewport.meshRenderObject._actor.GetProperty().SetRepresentationToWireframe()
