from typing import Any
from dataModel import ModelDatabase

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
