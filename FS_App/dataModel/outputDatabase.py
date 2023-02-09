from collections.abc import Sequence
from dataModel.mesh import Mesh

class OutputDatabase:
    '''
    Definition of an output database.
    '''

    @property
    def filePath(self) -> str:
        '''Output database file path.'''
        return self._filePath

    @filePath.setter
    def filePath(self, value: str) -> None:
        '''Output database file path (setter).'''
        self._filePath = value

    @property
    def mesh(self) -> Mesh:
        '''Output database finite element mesh.'''
        return self._mesh

    # attribute slots
    __slots__ = ('_filePath', '_mesh', '_frameDescriptions', '_data')

    def __init__(
        self,
        mesh: Mesh,
        frameDescriptions: Sequence[str],
        specs: Sequence[str],
        values: Sequence[Sequence[float]]
    ) -> None:
        '''Output database constructor.'''
        self._filePath: str = ''
        self._mesh: Mesh = mesh
        self._frameDescriptions: tuple[str, ...] = tuple(frameDescriptions)
        self._data: dict[int, dict[str, dict[str, tuple[float, ...]]]] = {}
        # convert input data
        for i, spec in enumerate(specs):
            frameString, groupName, fieldName = spec.split(':')
            frame: int = int(frameString)
            if frame not in self._data: self._data[frame] = {}
            if groupName not in self._data[frame]: self._data[frame][groupName] = {}
            self._data[frame][groupName][fieldName] = tuple(x[i] for x in values)

    def frameDescription(self, frame: int) -> str:
        '''Returns the frame description.'''
        return self._frameDescriptions[frame - 1]

    def frameNumbers(self) -> tuple[int, ...]:
        '''Returns the ordered frame numbers.'''
        return tuple(sorted(self._data.keys()))

    def nodalScalarFieldGroupNames(self, frame: int) -> tuple[str, ...]:
        '''Returns the nodal scalar field group names in the specified frame.'''
        return tuple(self._data[frame].keys())

    def nodalScalarFieldNames(self, frame: int, groupName: str) -> tuple[str, ...]:
        '''Returns the nodal scalar field names in the specified group.'''
        return tuple(self._data[frame][groupName].keys())

    def nodalScalarField(self, frame: int, groupName: str, fieldName: str) -> tuple[float, ...]:
        '''Returns the nodal scalar field values.'''
        return self._data[frame][groupName][fieldName]
