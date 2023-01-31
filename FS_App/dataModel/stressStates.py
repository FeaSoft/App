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
    C3D = StressState(103, '3D General Case') # 3D continuum (solid) general case
