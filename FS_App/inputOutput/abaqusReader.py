from os import path
from typing import cast
from dataModel import ModelingSpaces, ElementTypes, Mesh, NodeSet, ElementSet, ModelDatabase

class AbaqusReader:
    '''
    Static IO class for reading an Abaqus input (*.inp) file.
    '''

    @staticmethod
    def getModelingSpace(nodeData: list[tuple[float, float, float]]) -> ModelingSpaces | None:
        '''Gets the corresponding modeling space given the nodal coordinates.'''
        modelingSpace: int = 0
        for dimension in range(3):
            for coordinates in nodeData:
                if coordinates[dimension] != 0.0:
                    modelingSpace += 1
                    break
        match modelingSpace:
            case 2: return ModelingSpaces.TwoDimensional
            case 3: return ModelingSpaces.ThreeDimensional
            case _: return None

    @staticmethod
    def getElementType(modelingSpace: ModelingSpaces | None, abaqusCommand: str) -> ElementTypes | None:
        '''Gets the corresponding finite element type given a modeling space and an Abaqus command.'''
        # get abaqus element type from abaqus command
        abaqusElementType: str = abaqusCommand.split('=')[1].split(',')[0].upper()

        # get finite element type based on modeling space and abaqus element type
        match modelingSpace:
            case ModelingSpaces.TwoDimensional:
                match abaqusElementType:
                    case 'CPS3' | 'CPE3' | 'CAX3':                               return ElementTypes.E2D3
                    case 'CPS4' | 'CPE4' | 'CAX4' | 'CPS4R' | 'CPE4R' | 'CAX4R': return ElementTypes.E2D4
                    case _:                                                      return None
            case ModelingSpaces.ThreeDimensional:
                match abaqusElementType:
                    case 'C3D4':           return ElementTypes.E3D4
                    case 'C3D5':           return ElementTypes.E3D5
                    case 'C3D6':           return ElementTypes.E3D6
                    case 'C3D8' | 'C3D8R': return ElementTypes.E3D8
                    case _:                return None
            case _: return None

    @staticmethod
    def readModelDatabase(filePath: str) -> ModelDatabase:
        '''Creates a new finite element model database from the specified Abaqus input (*.inp) file.'''
        # initialize variables
        fs_mdb: str = path.splitext(filePath)[0] + '.fs_mdb' # the model database file (for storage)
        modelDatabase: ModelDatabase | None = None           # the new model database
        command: str = '...'                                 # the Abaqus command being parsed
        modelingSpace: ModelingSpaces | None = None          # the current modeling space
        elementType: ElementTypes | None = None              # the type of element being parsed
        nodeData: list[tuple[float, float, float]] = []      # the node data
        elementData: list[tuple[str, tuple[int, ...]]] = []  # the element data
        nodeSet: NodeSet | None = None                       # the node set being parsed
        elementSet: ElementSet | None = None                 # the element set being parsed
        generate: bool = False                               # specifies if the set being parsed is to be generated

        # read file line by line and parse its data
        with open(filePath, 'r') as file:
            for line in file:
                line = line.strip().replace(' ', '').lower()   # remove line ends and whitespaces; convert to lower case
                if len(line) > 0 and line[-1] == ',': line = line[:-1]                          # remove trailing commas
                if line == '' or (len(line) > 1 and line[:2] == '**'): continue          # skip empty lines and comments

                # parse command or its data
                if line[0] == '*':
                    # parse Abaqus command
                    command = (
                        'node'        if '*node'    in line else # parse nodes in following loop iterations
                        'element'     if '*element' in line else # parse elements in following loop iterations
                        'node-set'    if '*nset'    in line else # parse node set in following loop iterations
                        'element-set' if '*elset'   in line else # parse element set in following loop iterations
                        '...'                                    # do nothing in following loop iterations
                    )

                    # if read element command, get element type if available
                    if command == 'element':
                        modelingSpace = AbaqusReader.getModelingSpace(nodeData)
                        elementType = AbaqusReader.getElementType(modelingSpace, line)

                    # if read node set or element set command, create the model database now
                    if command in ('node-set', 'element-set') and not modelDatabase:
                        if not modelingSpace: raise RuntimeError('unsupported modeling space')
                        modelDatabase = ModelDatabase(Mesh(modelingSpace, nodeData, elementData))

                    # if read node set command, create a new node set
                    if command == 'node-set' and modelDatabase:
                        nodeSet = cast(NodeSet, modelDatabase.nodeSets.new())
                        name: str = line.split(',')[1].split('=')[1]
                        try:
                            nodeSet.name = name
                        except:
                            i: int = 2
                            while name + f'_{i}' in modelDatabase.nodeSets.names():
                                i += 1
                            nodeSet.name = name + f'_{i}'
                        generate = ',generate' in line
                    else: nodeSet = None

                    # if read element set command, create a new element set
                    if command == 'element-set' and modelDatabase:
                        elementSet = cast(ElementSet, modelDatabase.elementSets.new())
                        name: str = line.split(',')[1].split('=')[1]
                        try:
                            elementSet.name = name
                        except:
                            i: int = 2
                            while name + f'_{i}' in modelDatabase.elementSets.names():
                                i += 1
                            elementSet.name = name + f'_{i}'
                        generate = ',generate' in line
                    else: elementSet = None
                else:
                    # parse data
                    match command:

                        # parse node
                        case 'node':
                            coordinates: list[float] = [float(x) for x in line.split(',')[1:]]
                            while len(coordinates) < 3: coordinates.append(0.0)
                            nodeData.append(tuple(coordinates))

                        # parse element
                        case 'element':
                            if elementType:
                                nodeIndices: list[int] = [int(x) - 1 for x in line.split(',')[1:]]
                                elementData.append((elementType.name, tuple(nodeIndices)))

                        # parse node set
                        case 'node-set':
                            if nodeSet:
                                if not generate:
                                    indices: list[int] = [int(x) - 1 for x in line.split(',')]
                                    nodeSet.add(indices)
                                else:
                                    parameters: list[int] = [int(x) for x in line.split(',')]
                                    start: int = parameters[0] - 1
                                    stop:  int = parameters[1] - 1
                                    step:  int = parameters[2] if len(parameters) > 2 else 1
                                    nodeSet.add(range(start, stop + 1, step))

                        # parse element set
                        case 'element-set':
                            if elementSet:
                                if not generate:
                                    indices: list[int] = [int(x) - 1 for x in line.split(',')]
                                    elementSet.add(indices)
                                else:
                                    parameters: list[int] = [int(x) for x in line.split(',')]
                                    start: int = parameters[0] - 1
                                    stop:  int = parameters[1] - 1
                                    step:  int = parameters[2] if len(parameters) > 2 else 1
                                    elementSet.add(range(start, stop + 1, step))

                        # do nothing
                        case _: pass

        # create model database if not done already
        if not modelDatabase:
            if not modelingSpace: raise RuntimeError('unsupported modeling space')
            modelDatabase = ModelDatabase(Mesh(modelingSpace, nodeData, elementData))

        # done reading
        modelDatabase.filePath = fs_mdb
        return modelDatabase

    # attribute slots
    __slots__ = ()
