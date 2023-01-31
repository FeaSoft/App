from collections.abc import Callable
from dataModel.dataObject import DataObject

class Section(DataObject):
    '''
    Definition of a section.
    '''

    @property
    def elementSetName(self) -> str:
        '''Name of the associated element set.'''
        return self._elementSetName

    @elementSetName.setter
    def elementSetName(self, value: str) -> None:
        '''Name of the associated element set (setter).'''
        self._elementSetName = value
        self.notifyPropertyChanged('elementSetName')

    @property
    def materialName(self) -> str:
        '''Name of the associated material.'''
        return self._materialName

    @materialName.setter
    def materialName(self, value: str) -> None:
        '''Name of the associated material (setter).'''
        self._materialName = value
        self.notifyPropertyChanged('materialName')

    @property
    def stressState(self) -> str:
        '''Stress state.'''
        return self._stressState

    @stressState.setter
    def stressState(self, value: str) -> None:
        '''Stress state (setter).'''
        self._stressState = value
        self.notifyPropertyChanged('stressState')

    @property
    def planeThickness(self) -> float:
        '''Plane thickness.'''
        return self._planeThickness

    @planeThickness.setter
    def planeThickness(self, value: float) -> None:
        '''Plane thickness (setter).'''
        self._planeThickness = value
        self.notifyPropertyChanged('planeThickness')

    # attribute slots
    __slots__ = ('_elementSetName', '_materialName', '_stressState', '_planeThickness')

    def __init__(
        self,
        nameGetter: Callable[[DataObject], str],
        nameSetter: Callable[[DataObject, str], None]
    ) -> None:
        '''Section constructor.'''
        super().__init__(nameGetter, nameSetter)
        self._elementSetName: str = '<Undefined>'
        self._materialName: str = '<Undefined>'
        self._stressState: str = '<Undefined>'
        self._planeThickness: float = 0.0
