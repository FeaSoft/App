from enum import Enum, unique

@unique
class ElementTypes(Enum):
    '''
    The available finite element types.
    Notice: values must match with Fortran source.
    '''
    E2D3 = 11 # 2D interpolation element with 3 nodes
    E2D4 = 12 # 2D interpolation element with 4 nodes
    E3D4 = 13 # 3D interpolation element with 4 nodes
    E3D5 = 14 # 3D interpolation element with 5 nodes
    E3D6 = 15 # 3D interpolation element with 6 nodes
    E3D8 = 16 # 3D interpolation element with 8 nodes
