# build command
# pyinstaller fs_preprocessor.py --clean --noconfirm --onefile --noconsole --hidden-import vtkmodules.all

import sys
from typing import cast
from datetime import datetime
from inputOutput import FSReader
from dataModel import (
    StressStates, NodeSet, ElementSet, Material, Section, ConcentratedLoad, BoundaryCondition, ModelDatabase, BodyLoad,
    Pressure, SurfaceTraction, SurfaceSet
)

# warning and error counters
warnings: int = 0
errors: int = 0

def log(text: str = '') -> None:
    '''Logs the specified text without buffering.'''
    print(text, flush=True)

def countElementsPerNode(modelDatabase: ModelDatabase) -> tuple[int, ...]:
    '''Counts the number of elements associated to each node.'''
    counts: list[int] = [0]*len(modelDatabase.mesh.nodes)
    for element in modelDatabase.mesh.elements:
        for nodeIndex in element.nodeIndices:
            counts[nodeIndex] += 1
    return tuple(counts)

def countSectionsPerElement(modelDatabase: ModelDatabase) -> tuple[int, ...]:
    '''Counts the number of sections associated to each element.'''
    counts: list[int] = [0]*len(modelDatabase.mesh.elements)
    for section in modelDatabase.sections.dataObjects():
        section = cast(Section, section)
        if section.elementSetName == '<Undefined>': continue
        elementSet = cast(ElementSet, modelDatabase.elementSets[section.elementSetName])
        for elementIndex in elementSet.indices():
            counts[elementIndex] += 1
    return tuple(counts)

def checkMesh(modelDatabase: ModelDatabase) -> None:
    '''Performs basic checks on the finite element mesh.'''
    global errors
    if 0 in countElementsPerNode(modelDatabase):
        errors += 1
        log(f"Error: unconnected node detected")
    if countSectionsPerElement(modelDatabase).count(1) != len(modelDatabase.mesh.elements):
        errors += 1
        log(f"Error: elements with undefined or over defined section detected")
    for element in modelDatabase.mesh.elements:
        if modelDatabase.mesh.modelingSpace != element.modelingSpace:
            errors += 1
            dimensionality: int = modelDatabase.mesh.modelingSpace.value
            log(f"Error: mesh is {dimensionality}D, but it contains non-{dimensionality}D elements")
            break

def checkNodeSets(modelDatabase: ModelDatabase) -> None:
    '''Performs basic checks on the node sets.'''
    global warnings
    for nodeSet in modelDatabase.nodeSets.dataObjects():
        nodeSet = cast(NodeSet, nodeSet)
        if nodeSet.count == 0:
            warnings += 1
            log(f"Warning: node set contains 0 nodes: '{nodeSet.name}'")

def checkElementSets(modelDatabase: ModelDatabase) -> None:
    '''Performs basic checks on the element sets.'''
    global warnings
    for elementSet in modelDatabase.elementSets.dataObjects():
        elementSet = cast(ElementSet, elementSet)
        if elementSet.count == 0:
            warnings += 1
            log(f"Warning: element set contains 0 elements: '{elementSet.name}'")

def checkSurfaceSets(modelDatabase: ModelDatabase) -> None:
    '''Performs basic checks on the surface sets.'''
    global warnings
    for surfaceSet in modelDatabase.surfaceSets.dataObjects():
        surfaceSet = cast(SurfaceSet, surfaceSet)
        if surfaceSet.count == 0:
            warnings += 1
            log(f"Warning: surface set contains 0 surfaces: '{surfaceSet.name}'")

def checkMaterials(modelDatabase: ModelDatabase) -> None:
    '''Performs basic checks on the materials.'''
    global errors
    for material in modelDatabase.materials.dataObjects():
        material = cast(Material, material)
        if material.young <= 0.0:
            errors += 1
            log(f"Error: material has a Young's modulus that is less than or equal to 0: '{material.name}'")
        if not (0.0 < material.poisson < 0.495):
            errors += 1
            log(f"Error: material has a Poisson's ratio outside of the range (0, 0.495): '{material.name}'")
        if material.density < 0.0:
            errors += 1
            log(f"Error: material has a mass density that is less than 0: '{material.name}'")

def checkSections(modelDatabase: ModelDatabase) -> None:
    '''Performs basic checks on the sections.'''
    global errors
    for section in modelDatabase.sections.dataObjects():
        section = cast(Section, section)
        if section.elementSetName == '<Undefined>':
            errors += 1
            log(f"Error: section with undefined element set: '{section.name}'")
        if section.materialName == '<Undefined>':
            errors += 1
            log(f"Error: section with undefined material: '{section.name}'")
        if section.stressState == '<Undefined>':
            errors += 1
            log(f"Error: section with undefined stress state: '{section.name}'")
        # allow this for axisymmetric
        # if modelDatabase.mesh.modelingSpace == ModelingSpaces.TwoDimensional and section.planeThickness <= 0.0:
        #     errors += 1
        #     log(f"Error: section has a plane thickness that is less than or equal to 0: '{section.name}'")

def checkConcentratedLoads(modelDatabase: ModelDatabase) -> None:
    '''Performs basic checks on the concentrated loads.'''
    global errors, warnings
    for concentratedLoad in modelDatabase.concentratedLoads.dataObjects():
        concentratedLoad = cast(ConcentratedLoad, concentratedLoad)
        if concentratedLoad.nodeSetName == '<Undefined>':
            errors += 1
            log(f"Error: concentrated load with undefined node set: '{concentratedLoad.name}'")
        if sum(abs(x) for x in concentratedLoad.components()) == 0.0:
            warnings += 1
            log(f"Warning: concentrated load has a magnitude of 0: '{concentratedLoad.name}'")

def checkPressures(modelDatabase: ModelDatabase) -> None:
    '''Performs basic checks on the pressures.'''
    global errors, warnings
    for pressure in modelDatabase.pressures.dataObjects():
        pressure = cast(Pressure, pressure)
        if pressure.surfaceSetName == '<Undefined>':
            errors += 1
            log(f"Error: pressure with undefined surface set: '{pressure.name}'")
        if pressure.magnitude == 0.0:
            warnings += 1
            log(f"Warning: pressure has a magnitude of 0: '{pressure.name}'")

def checkSurfaceTractions(modelDatabase: ModelDatabase) -> None:
    '''Performs basic checks on the surface tractions.'''
    global errors, warnings
    for surfaceTraction in modelDatabase.surfaceTractions.dataObjects():
        surfaceTraction = cast(SurfaceTraction, surfaceTraction)
        if surfaceTraction.surfaceSetName == '<Undefined>':
            errors += 1
            log(f"Error: surface traction with undefined surface set: '{surfaceTraction.name}'")
        if sum(abs(x) for x in surfaceTraction.components()) == 0.0:
            warnings += 1
            log(f"Warning: surface traction has a magnitude of 0: '{surfaceTraction.name}'")

def checkBodyLoads(modelDatabase: ModelDatabase) -> None:
    '''Performs basic checks on the body loads.'''
    global errors, warnings
    # get element section indices
    elementSectionIndices: list[int] = [0]*len(modelDatabase.mesh.elements)
    for sectionIndex, section in enumerate(modelDatabase.sections.dataObjects()):
        section = cast(Section, section)
        elementSet = cast(ElementSet, modelDatabase.elementSets[section.elementSetName])
        for elementIndex in elementSet.indices():
            elementSectionIndices[elementIndex] = sectionIndex
    # check
    for bodyLoad in modelDatabase.bodyLoads.dataObjects():
        bodyLoad = cast(BodyLoad, bodyLoad)
        if bodyLoad.elementSetName == '<Undefined>':
            errors += 1
            log(f"Error: body load with undefined element set: '{bodyLoad.name}'")
        if bodyLoad.type == '<Undefined>':
            errors += 1
            log(f"Error: body load with undefined type: '{bodyLoad.name}'")
        if sum(abs(x) for x in bodyLoad.components()) == 0.0:
            warnings += 1
            log(f"Warning: body load has a magnitude of 0: '{bodyLoad.name}'")
    for bodyLoad in modelDatabase.bodyLoads.dataObjects():
        bodyLoad = cast(BodyLoad, bodyLoad)
        if bodyLoad.type == 'Acceleration' and bodyLoad.elementSetName != '<Undefined>':
            elementSet = cast(ElementSet, modelDatabase.elementSets[bodyLoad.elementSetName])
            for i in elementSet.indices():
                section = cast(Section, modelDatabase.sections.dataObjects()[elementSectionIndices[i]])
                material = cast(Material, modelDatabase.materials[section.materialName])
                if material.density == 0.0:
                    errors += 1
                    log(f"Error: 'Acceleration' body load contains elements with 0 mass density: '{bodyLoad.name}'")
                    return

def checkBoundaryConditions(modelDatabase: ModelDatabase) -> None:
    '''Performs basic checks on the boundary conditions.'''
    global errors, warnings
    for boundaryCondition in modelDatabase.boundaryConditions.dataObjects():
        boundaryCondition = cast(BoundaryCondition, boundaryCondition)
        if boundaryCondition.nodeSetName == '<Undefined>':
            errors += 1
            log(f"Error: boundary condition with undefined node set: '{boundaryCondition.name}'")
        if True not in boundaryCondition.activeDOFs():
            warnings += 1
            log(f"Warning: boundary condition has no active degrees of freedom: '{boundaryCondition.name}'")

def writeSolverJobInputFile(modelDatabase: ModelDatabase, solverJobInputFile: str) -> None:
    '''Writes the solver job input file.'''
    with open(solverJobInputFile, 'w') as file:
        # get element section indices
        elementSectionIndices: list[int] = [0]*len(modelDatabase.mesh.elements)
        for sectionIndex, section in enumerate(modelDatabase.sections.dataObjects()):
            section = cast(Section, section)
            elementSet = cast(ElementSet, modelDatabase.elementSets[section.elementSetName])
            for elementIndex in elementSet.indices():
                elementSectionIndices[elementIndex] = sectionIndex + 1 # 1-based indexing
        # mesh
        file.write('mesh' + '\n')
        file.write(str(len(modelDatabase.mesh.nodes)) + ',')
        file.write(str(len(modelDatabase.mesh.elements)) + ',')
        file.write(str(modelDatabase.mesh.modelingSpace.value) + '\n')
        # nodes
        file.write('nodes' + '\n')
        for node in modelDatabase.mesh.nodes:
            file.write(f'{node.x},{node.y},{node.z}' + '\n')
        # elements
        file.write('elements' + '\n')
        for element, elementSectionIndex in zip(modelDatabase.mesh.elements, elementSectionIndices):
            file.write(f"{element.elementType.value},{elementSectionIndex},")
            file.write(','.join(str(x + 1) for x in element.nodeIndices) + '\n') # 1-based indexing
        # model database
        file.write('database' + '\n')
        file.write(str(len(modelDatabase.nodeSets)) + ',')
        file.write(str(len(modelDatabase.elementSets)) + ',')
        file.write(str(len(modelDatabase.surfaceSets)) + ',')
        file.write(str(len(modelDatabase.materials)) + ',')
        file.write(str(len(modelDatabase.sections)) + ',')
        file.write(str(len(modelDatabase.concentratedLoads)) + ',')
        file.write(str(len(modelDatabase.pressures) + len(modelDatabase.surfaceTractions)) + ',')
        file.write(str(len(modelDatabase.bodyLoads)) + ',')
        file.write(str(len(modelDatabase.boundaryConditions)) + '\n')
        # node sets
        for nodeSet in modelDatabase.nodeSets.dataObjects():
            nodeSet = cast(NodeSet, nodeSet)
            file.write('node-set' + '\n')
            file.write(str(nodeSet.count) + '\n')
            for index in nodeSet.indices():
                file.write(str(index + 1) + '\n') # 1-based indexing
        # element sets
        for elementSet in modelDatabase.elementSets.dataObjects():
            elementSet = cast(ElementSet, elementSet)
            file.write('element-set' + '\n')
            file.write(str(elementSet.count) + '\n')
            for index in elementSet.indices():
                file.write(str(index + 1) + '\n') # 1-based indexing
        # surface sets
        for surfaceSet in modelDatabase.surfaceSets.dataObjects():
            surfaceSet = cast(SurfaceSet, surfaceSet)
            file.write('surface-set' + '\n')
            file.write(str(surfaceSet.count) + '\n')
            for surface in surfaceSet.surfaces():
                elementIndex, connectivity = surface
                file.write(str(elementIndex + 1) + ',') # 1-based indexing
                file.write(str(len(connectivity)))
                for index in connectivity: file.write(',' + str(index + 1)) # 1-based indexing
                file.write('\n')
        # materials
        for material in modelDatabase.materials.dataObjects():
            material = cast(Material, material)
            file.write('material' + '\n')
            file.write(f'{material.young},{material.poisson},{material.density}' + '\n')
        # sections
        for section in modelDatabase.sections.dataObjects():
            section = cast(Section, section)
            elementSet = cast(ElementSet, modelDatabase.elementSets[section.elementSetName])
            material = cast(Material, modelDatabase.materials[section.materialName])
            file.write('section' + '\n')
            file.write(str(StressStates.fromName(section.stressState).value) + ',')
            file.write(str(elementSet.index + 1) + ',')
            file.write(str(material.index + 1) + ',')
            file.write(str(section.planeThickness) + '\n')
        # concentrated loads
        for concentratedLoad in modelDatabase.concentratedLoads.dataObjects():
            concentratedLoad = cast(ConcentratedLoad, concentratedLoad)
            nodeSet = cast(NodeSet, modelDatabase.nodeSets[concentratedLoad.nodeSetName])
            file.write('concentrated-load' + '\n')
            file.write(f'{nodeSet.index + 1},{concentratedLoad.x},{concentratedLoad.y},{concentratedLoad.z}' + '\n')
        # surface loads
        for pressure in modelDatabase.pressures.dataObjects():
            pressure = cast(Pressure, pressure)
            surfaceSet = cast(SurfaceSet, modelDatabase.surfaceSets[pressure.surfaceSetName])
            file.write('surface-load' + '\n')
            file.write(f'{surfaceSet.index + 1},P,{pressure.magnitude},0.0,0.0' + '\n')
        for surfaceTraction in modelDatabase.surfaceTractions.dataObjects():
            surfaceTraction = cast(SurfaceTraction, surfaceTraction)
            surfaceSet = cast(SurfaceSet, modelDatabase.surfaceSets[surfaceTraction.surfaceSetName])
            file.write('surface-load' + '\n')
            file.write(f'{surfaceSet.index + 1},T,{surfaceTraction.x},{surfaceTraction.y},{surfaceTraction.z}' + '\n')
        # body loads
        for bodyLoad in modelDatabase.bodyLoads.dataObjects():
            bodyLoad = cast(BodyLoad, bodyLoad)
            elementSet = cast(ElementSet, modelDatabase.elementSets[bodyLoad.elementSetName])
            bodyLoadType: str = 'A' if bodyLoad.type == 'Acceleration' else 'F'
            file.write('body-load' + '\n')
            file.write(f'{elementSet.index + 1},{bodyLoadType},{bodyLoad.x},{bodyLoad.y},{bodyLoad.z}' + '\n')
        # boundary conditions
        for boundaryCondition in modelDatabase.boundaryConditions.dataObjects():
            boundaryCondition = cast(BoundaryCondition, boundaryCondition)
            nodeSet = cast(NodeSet, modelDatabase.nodeSets[boundaryCondition.nodeSetName])
            file.write('boundary-condition' + '\n')
            file.write(f'{nodeSet.index + 1},{boundaryCondition.x},{boundaryCondition.y},{boundaryCondition.z}' + ',')
            file.write(('T' if boundaryCondition.isActiveInX else 'F') + ',')
            file.write(('T' if boundaryCondition.isActiveInY else 'F') + ',')
            file.write(('T' if boundaryCondition.isActiveInZ else 'F') + '\n')

if __name__ == '__main__':
    # unpack arguments
    modelDatabaseFile, solverJobInputFile, logFile = sys.argv[:3]

    # redirect standard output and error streams
    sys.tracebacklimit = int(sys.argv[3])
    sys.stdout = open(logFile, 'w')
    sys.stderr = sys.stdout

    # log start
    log('Preprocessor has started')
    log(datetime.now().isoformat(sep=' ', timespec='seconds'))
    log()

    # load model database from file
    log(f"Loading model database from file: '{modelDatabaseFile}'")
    modelDatabase: ModelDatabase = FSReader.readModelDatabase(modelDatabaseFile)
    log('Model database loaded')
    log()

    # perform basic checks
    log('Checking the model definition')
    checkMesh(modelDatabase)
    checkNodeSets(modelDatabase)
    checkElementSets(modelDatabase)
    checkSurfaceSets(modelDatabase)
    checkMaterials(modelDatabase)
    checkSections(modelDatabase)
    checkConcentratedLoads(modelDatabase)
    checkPressures(modelDatabase)
    checkSurfaceTractions(modelDatabase)
    checkBodyLoads(modelDatabase)
    checkBoundaryConditions(modelDatabase)
    if warnings > 0: log(f'Model definition contains {warnings} warning(s)')
    if errors > 0: log(f'Model definition contains {errors} error(s)')
    if warnings == 0 and errors == 0: log('Basic checks found no warnings nor errors')
    log()

    # write solver job input file
    if errors > 0:
        log('Solver job input file not written due to errors in the model definition')
    else:
        log('Writing solver job input file')
        writeSolverJobInputFile(modelDatabase, solverJobInputFile)
        log('Solver job input file written')
    log()

    # done
    log('Preprocessor is done')
    sys.stdout.close()
    sys.exit(errors)
