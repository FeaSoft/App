import sys
from typing import cast
from datetime import datetime
from inputOutput import FSReader
from dataModel import (
    ModelingSpaces, StressStates, NodeSet, ElementSet, Material, Section, ConcentratedLoad, BoundaryCondition, ModelDatabase
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
        if modelDatabase.mesh.modelingSpace == ModelingSpaces.TwoDimensional and section.planeThickness <= 0.0:
            errors += 1
            log(f"Error: section has a plane thickness that is less than or equal to 0: '{section.name}'")

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
        file.write(str(len(modelDatabase.materials)) + ',')
        file.write(str(len(modelDatabase.sections)) + ',')
        file.write(str(len(modelDatabase.concentratedLoads)) + ',')
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
    modelDatabaseFile, solverJobInputFile, logFile = sys.argv[1:4]

    # redirect standard output and error streams
    sys.tracebacklimit = int(sys.argv[4])
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
    checkMaterials(modelDatabase)
    checkSections(modelDatabase)
    checkConcentratedLoads(modelDatabase)
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



# #         private static void CheckSurfaceSets(ModelDatabase model)
# #         {
# #             foreach (SurfaceSet surfaceSet in model.SurfaceSets)
# #                 if (surfaceSet.Count == 0)
# #                 {
# #                     warnings++;
# #                     Solver.Output.Add($"Warning: Surface set '{surfaceSet.Name}' contains 0 surfaces.");
# #                 }
# #         }
# #         private static void CheckSurfaceLoads(ModelDatabase model)
# #         {
# #             foreach (SurfaceLoad sload in model.SurfaceLoads)
# #             {
# #                 if (sload.SurfaceSet == null)
# #                 {
# #                     errors++;
# #                     Solver.Output.Add($"Error: Surface load '{sload.Name}' with undefined surface set.");
# #                 }
# #                 if (sload.Magnitude == 0.0 || (!sload.IsPressure && sload.Direction == (0.0, 0.0, 0.0)))
# #                 {
# #                     warnings++;
# #                     Solver.Output.Add($"Warning: Surface load '{sload.Name}' has a magnitude of 0.");
# #                 }
# #             }
# #         }
# #         private static void CheckBodyLoads(ModelDatabase model)
# #         {
# #             foreach (BodyLoad bload in model.BodyLoads)
# #             {
# #                 if (bload.ElementSet == null)
# #                 {
# #                     errors++;
# #                     Solver.Output.Add($"Error: Body load '{bload.Name}' with undefined element set.");
# #                 }
# #                 if (bload.X == 0.0 && bload.Y == 0.0 && bload.Z == 0.0)
# #                 {
# #                     warnings++;
# #                     Solver.Output.Add($"Warning: Body load '{bload.Name}' has a magnitude of 0.");
# #                 }
# #             }
# #             foreach (BodyLoad bload in model.BodyLoads)
# #                 if (bload.IsGravity && bload.ElementSet is ElementSet elementSet)
# #                     foreach (Element element in elementSet)
# #                         if (element.Section is Section section && section.Material is Material material && material.Density == 0.0)
# #                         {
# #                             errors++;
# #                             Solver.Output.Add($"Error: Body load '{bload.Name}' is of type gravity while containing elements with a mass density of 0.");
# #                             return;
# #                         }
# #         }
# #         private static void CheckFrequencyAnalysis(ModelDatabase model)
# #         {
# #             if (Solver.Options.AnalysisType != AnalysisType.Frequency) return;

# #             foreach (Element element in model.Mesh.Elements)
# #                 if (element.Section is Section section && section.Material is Material material && material.Density == 0.0)
# #                 {
# #                     errors++;
# #                     Solver.Output.Add("Error: In a frequency analysis the mass density must be specified for all elements.");
# #                     break;
# #                 }

# #             if (Solver.Options.RequestedNumberOfEigenpairs > model.Mesh.Nodes.Count)
# #             {
# #                 errors++;
# #                 Solver.Output.Add("Error: The requested number of eigenpairs is too large.");
# #             }

# #             if (Solver.Options.RequestedNumberOfEigenpairs > 100)
# #             {
# #                 warnings++;
# #                 Solver.Output.Add("Warning: A large number of eigenpairs was requested (>100).");
# #             }

# #             if (model.ConcentratedLoads.Count > 0 || model.SurfaceLoads.Count > 0 || model.BodyLoads.Count > 0)
# #             {
# #                 warnings++;
# #                 Solver.Output.Add("Warning: In a frequency analysis any type of loading is ignored.");
# #             }

# #             foreach (BoundaryCondition boundary in model.BoundaryConditions)
# #                 if (boundary.X != 0.0 || boundary.Y != 0.0 || boundary.Z != 0.0)
# #                 {
# #                     warnings++;
# #                     Solver.Output.Add("Warning: In a frequency analysis any imposed displacement is assumed to be 0.");
# #                     break;
# #                 }
# #         }
