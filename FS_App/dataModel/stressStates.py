from dataclasses import dataclass

@dataclass(frozen=True)
class StressState:
    '''
    Definition of a stress state.
    '''
    value: int
    name: str

class StressStates:
    '''
    The available stress states.
    Notice: values must match with Fortran source.
    '''
    CPS = StressState(101, '2D Plane Stress') # 2D continuum (solid) plane stress
    CPE = StressState(102, '2D Plane Strain') # 2D continuum (solid) plane strain
    CAX = StressState(103, '2D Axisymmetric') # 2D continuum (solid) axisymmetric
    C3D = StressState(104, '3D General Case') # 3D continuum (solid) general case
    _stressStates: tuple[StressState, ...] = (CPS, CPE, CAX, C3D)

    @classmethod
    def fromName(cls, name: str) -> StressState:
        '''Returns the stress state with the given name.'''
        for stressState in cls._stressStates:
            if stressState.name == name:
                return stressState
        raise ValueError('invalid name')
