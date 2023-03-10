from typing import Any
from dataModel import ModelDatabase, OutputDatabase

class FSReader:
    '''
    Static IO class for reading FeaSoft files.
    '''

    @staticmethod
    def readModelDatabase(filePath: str) -> ModelDatabase:
        '''Reads the model database from the specified file.'''
        variables: dict[str, Any] = {}
        with open(filePath, 'r') as file:
            exec(file.read(), variables)
        if 'modelDatabase' in variables and isinstance(variables['modelDatabase'], ModelDatabase):
            variables['modelDatabase'].filePath = filePath
            return variables['modelDatabase']
        raise RuntimeError(f"could not interpret model database from file: '{filePath}'")

    @staticmethod
    def readOutputDatabase(filePath: str) -> OutputDatabase:
        '''Reads the output database from the specified file.'''
        variables: dict[str, Any] = {}
        with open(filePath, 'r') as file:
            exec(file.read(), variables)
        if 'outputDatabase' in variables and isinstance(variables['outputDatabase'], OutputDatabase):
            variables['outputDatabase'].filePath = filePath
            return variables['outputDatabase']
        raise RuntimeError(f"could not interpret output database from file: '{filePath}'")
