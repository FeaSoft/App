from enum import Enum, unique

@unique
class InteractionStyles(Enum):
    '''
    Available viewport interaction styles.
    '''
    Rotate       = 0
    Pan          = 1
    Zoom         = 2
    PickSingle   = 3
    PickMultiple = 4
    Probe        = 5
