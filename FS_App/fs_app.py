if __name__ == '__main__':
    import sys
    import application

    # redirect standard streams
    sys.tracebacklimit = 0
    sys.stdout = application.current.mainWindow.terminal.stdout
    sys.stderr = application.current.mainWindow.terminal.stderr
    sys.stdin  = application.current.mainWindow.terminal.stdin

    # start the application event loop
    sys.exit(application.current.start())
