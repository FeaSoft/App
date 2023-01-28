from enum import Enum, unique

@unique
class ModelingSpaces(Enum):
    '''
    Available modeling spaces.
    '''
    TwoDimensional   = 2 # two-dimensional (2D) modeling space
    ThreeDimensional = 3 # three-dimensional (3D) modeling space
