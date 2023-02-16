from typing import Sequence
from subprocess import Popen as Process, CREATE_NO_WINDOW
from psutil import Process as ProcessInfo, cpu_count
from io import TextIOWrapper

class Subprocess:
    '''
    Utility class for creating and managing subprocesses.
    '''

    # attribute slots
    __slots__ = ('_process', '_info')

    def __init__(self) -> None:
        '''Subprocess constructor.'''
        self._process: Process[bytes] | None = None
        self._info: ProcessInfo | None = None

    def isAlive(self) -> bool:
        '''Determines if the process is currently alive.'''
        if self._process and self._info and self._info.is_running():
            return True
        return False

    def cpuPercentage(self) -> int:
        '''Returns the current CPU usage in percentage.'''
        if self._process and self._info and self._info.is_running():
            return round(self._info.cpu_percent()/cpu_count())
        return 0

    def memory(self) -> int:
        '''Returns the current physical memory usage in MB.'''
        if self._process and self._info and self._info.is_running():
            return round(self._info.memory_info().rss * 1e-6)
        return 0

    def cpuTime(self) -> float:
        '''Returns the current CPU time in seconds.'''
        if self._process and self._info and self._info.is_running():
            userTime: float = self._info.cpu_times().user
            systemTime: float = self._info.cpu_times().system
            return round(userTime + systemTime, 3)
        return 0

    def start(
        self, exe: str,
        args: Sequence[str],
        stdout: TextIOWrapper | None = None,
        stderr: TextIOWrapper | None = None
    ) -> None:
        '''Starts the specified process.'''
        if self._process and self._info: self.terminate()
        self._process = Process(
            executable=exe,
            args=' '.join(args),
            stdout=stdout,
            stderr=stderr,
            creationflags=CREATE_NO_WINDOW
        )
        self._info = ProcessInfo(self._process.pid)

    def terminate(self) -> None:
        '''Terminates the process if it is running.'''
        if self._process and self._info:
            self._process.terminate()
            self._process = None
            self._info = None

    def exitCode(self) -> int | None:
        '''Returns the exit code if the process has exited successfully.'''
        if self._process and self._info and not self._info.is_running():
            return self._process.poll()
        return None
