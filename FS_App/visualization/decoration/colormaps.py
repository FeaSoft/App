from enum import Enum, unique

@unique
class Colormaps(Enum):
    '''
    Available colormaps.
    '''
    Jet       = 0
    Rainbow   = 1
    Cyclic    = 2
    Parula    = 3
    Viridis   = 4
    Plasma    = 5
    Marc      = 6
    Linear    = 7
    Diverging = 8
    Grayscale = 9
