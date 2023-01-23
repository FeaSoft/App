from collections.abc import Callable
from dataModel.dataObject import DataObject

class Material(DataObject):
    '''
    Definition of a material.
    '''

    @property
    def young(self) -> float:
        '''Young's modulus.'''
        return self._young

    @young.setter
    def young(self, value: float) -> None:
        '''Young's modulus (setter).'''
        self._young = value
        self._notifyPropertyChanged('young')

    @property
    def poisson(self) -> float:
        '''Poisson's ratio.'''
        return self._poisson

    @poisson.setter
    def poisson(self, value: float) -> None:
        '''Poisson's ratio (setter).'''
        self._poisson = value
        self._notifyPropertyChanged('poisson')

    @property
    def density(self) -> float:
        '''Mass density.'''
        return self._density

    @density.setter
    def density(self, value: float) -> None:
        '''Mass density (setter).'''
        self._density = value
        self._notifyPropertyChanged('density')

    # attribute slots
    __slots__ = ('_young', '_poisson', '_density')

    def __init__(
        self,
        nameGetter: Callable[[DataObject], str],
        nameSetter: Callable[[DataObject, str], None]
    ) -> None:
        '''Material constructor.'''
        super().__init__(nameGetter, nameSetter)
        self._young: float = 0.0
        self._poisson: float = 0.0
        self._density: float = 0.0
