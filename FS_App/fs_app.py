if __name__ == '__main__':
    import sys
    import application

    # redirect standard streams
    sys.tracebacklimit = 0
    sys.stdout = application.current.mainWindow.terminal.stdout
    sys.stderr = application.current.mainWindow.terminal.stderr
    sys.stdin  = application.current.mainWindow.terminal.stdin

    # start the application event loop
    exitCode: int = application.current.start()

    # reset streams
    sys.stdout = sys.__stdout__
    sys.stderr = sys.__stderr__
    sys.stdin  = sys.__stdin__

    # exit application
    sys.exit(exitCode)
