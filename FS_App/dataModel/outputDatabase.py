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

    @property
    def frameCount(self) -> int:
        '''Number of output frames.'''
        return self._frameCount

    # attribute slots
    __slots__ = ('_filePath', '_mesh', '_frameCount', '_frameDescriptions', '_historyData', '_fieldData')

    def __init__(
        self,
        mesh: Mesh,
        frameCount: int,
        frameDescriptions: Sequence[str],
        historyOutputDescriptions: Sequence[str],
        fieldOutputDescriptions: Sequence[str],
        historyOutput: Sequence[Sequence[float]],
        fieldOutput: Sequence[Sequence[Sequence[float]]]
    ) -> None:
        '''Output database constructor.'''
        self._filePath: str = ''
        self._mesh: Mesh = mesh
        self._frameCount: int = frameCount
        self._frameDescriptions: tuple[str, ...] = tuple(frameDescriptions[0:frameCount])
        self._historyData: tuple[dict[str, float], ...] = tuple({} for _ in range(frameCount))
        self._fieldData: tuple[dict[str, dict[str, tuple[float, ...]]], ...] = tuple({} for _ in range(frameCount))
        # convert input data
        for frame in range(frameCount):
            # convert history output data
            for i, description in enumerate(historyOutputDescriptions):
                self._historyData[frame][description] = historyOutput[frame][i]
            # convert field output data
            for i, description in enumerate(fieldOutputDescriptions):
                groupName, fieldName = description.split(':')
                if groupName not in self._fieldData[frame]: self._fieldData[frame][groupName] = {}
                self._fieldData[frame][groupName][fieldName] = tuple(x[i] for x in fieldOutput[frame])

    def nodalDisplacements(self, frame: int) -> tuple[tuple[float, float, float], ...]:
        '''Returns the nodal displacements for the specified frame.'''
        if 'Displacement' in self._fieldData[frame]:
            if all(x in self._fieldData[frame]['Displacement'] for x in (
                'Displacement in X', 'Displacement in Y', 'Displacement in Z'
            )):
                return tuple((
                    self._fieldData[frame]['Displacement']['Displacement in X'][i],
                    self._fieldData[frame]['Displacement']['Displacement in Y'][i],
                    self._fieldData[frame]['Displacement']['Displacement in Z'][i],
                ) for i in range(len(self._mesh.nodes)))
        raise RuntimeError('output database does not contain nodal displacements')

    def frameDescription(self, frame: int) -> str:
        '''Returns the frame description.'''
        return self._frameDescriptions[frame]

    def nodalScalarFieldGroupNames(self, frame: int) -> tuple[str, ...]:
        '''Returns the nodal scalar field group names in the specified frame.'''
        return tuple(self._fieldData[frame].keys())

    def nodalScalarFieldNames(self, frame: int, groupName: str) -> tuple[str, ...]:
        '''Returns the nodal scalar field names in the specified group.'''
        return tuple(self._fieldData[frame][groupName].keys())

    def nodalScalarField(self, frame: int, groupName: str, fieldName: str) -> tuple[float, ...]:
        '''Returns the nodal scalar field values.'''
        return self._fieldData[frame][groupName][fieldName]

    def historyNames(self, frame: int) -> tuple[str, ...]:
        '''Returns the history names in the specified frame.'''
        return tuple(self._historyData[frame].keys())

    def history(self, frame: int, historyName: str) -> float:
        '''Returns the history value.'''
        return self._historyData[frame][historyName]
