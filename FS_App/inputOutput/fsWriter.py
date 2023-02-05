from typing import cast
from datetime import datetime
from dataModel import NodeSet, ElementSet, Material, Section, ConcentratedLoad, BoundaryCondition, ModelDatabase

class FSWriter:
    '''
    Static IO class for writing FeaSoft files.
    '''

    @staticmethod
    def writeModelDatabase(modelDatabase: ModelDatabase) -> None:
        '''Writes the specified model database to file.'''
        comment: str = '# '
        separator: str = comment + '='*(80 - len(comment))
        indentation: str = ' '*4
        with open(modelDatabase.filePath, 'w') as file:
            # header and imports
            file.write(separator + '\n')
            file.write(comment + 'MODEL DATABASE GENERATED BY FEASOFT' + '\n')
            file.write(comment + datetime.now().isoformat(sep=' ', timespec='seconds') + '\n')
            file.write(separator + '\n')
            file.write('from dataModel import *' + '\n')
            file.write('\n')
            # nodes
            file.write(separator + '\n')
            file.write(comment + 'NODAL COORDINATES' + '\n')
            file.write(separator + '\n')
            file.write('nodeData = (' + '\n')
            for node in modelDatabase.mesh.nodes:
                file.write(indentation + str(node.coordinates) + ',' + '\n')
            file.write(')' + '\n')
            file.write('\n')
            # elements
            file.write(separator + '\n')
            file.write(comment + 'ELEMENT CONNECTIVITY' + '\n')
            file.write(separator + '\n')
            file.write('elementData = (' + '\n')
            for element in modelDatabase.mesh.elements:
                file.write(
                    indentation + "('" + element.elementType.name + "', " + str(element.nodeIndices) + '),' + '\n'
                )
            file.write(')' + '\n')
            file.write('\n')
            # mesh
            file.write(separator + '\n')
            file.write(comment + 'FINITE ELEMENT MESH' + '\n')
            file.write(separator + '\n')
            file.write(f'mesh = Mesh({modelDatabase.mesh.modelingSpace.value}, nodeData, elementData)' + '\n')
            file.write('\n')
            # model database
            file.write(separator + '\n')
            file.write(comment + 'MODEL DATABASE' + '\n')
            file.write(separator + '\n')
            file.write('modelDatabase = ModelDatabase(mesh)' + '\n')
            file.write('\n')
            # node sets
            if len(modelDatabase.nodeSets) > 0:
                file.write(separator + '\n')
                file.write(comment + 'NODE SETS' + '\n')
                file.write(separator + '\n')
                for i, nodeSet in enumerate(modelDatabase.nodeSets.dataObjects()):
                    nodeSet = cast(NodeSet, nodeSet)
                    file.write(f'nodeSet{i + 1} = modelDatabase.nodeSets.new()' + '\n')
                    file.write(f"nodeSet{i + 1}.name = '{nodeSet.name}'" + '\n')
                    if nodeSet.count > 0:
                        file.write(f'nodeSet{i + 1}.add(' + '\n')
                        file.write(indentation + '(')
                        for k, index in enumerate(nodeSet.indices()):
                            if k % 10 == 0: file.write('\n' + indentation*2)
                            file.write(str(index) + ', ')
                        file.write('\n' + indentation + ')' + '\n')
                        file.write(f')' + '\n')
                    file.write('\n')
            # element sets
            if len(modelDatabase.elementSets) > 0:
                file.write(separator + '\n')
                file.write(comment + 'ELEMENT SETS' + '\n')
                file.write(separator + '\n')
                for i, elementSet in enumerate(modelDatabase.elementSets.dataObjects()):
                    elementSet = cast(ElementSet, elementSet)
                    file.write(f'elementSet{i + 1} = modelDatabase.elementSets.new()' + '\n')
                    file.write(f"elementSet{i + 1}.name = '{elementSet.name}'" + '\n')
                    if elementSet.count > 0:
                        file.write(f'elementSet{i + 1}.add(' + '\n')
                        file.write(indentation + '(')
                        for k, index in enumerate(elementSet.indices()):
                            if k % 10 == 0: file.write('\n' + indentation*2)
                            file.write(str(index) + ', ')
                        file.write('\n' + indentation + ')' + '\n')
                        file.write(f')' + '\n')
                    file.write('\n')
            # materials
            if len(modelDatabase.materials) > 0:
                file.write(separator + '\n')
                file.write(comment + 'MATERIALS' + '\n')
                file.write(separator + '\n')
                for i, material in enumerate(modelDatabase.materials.dataObjects()):
                    material = cast(Material, material)
                    file.write(f'material{i + 1} = modelDatabase.materials.new()' + '\n')
                    file.write(f"material{i + 1}.name = '{material.name}'" + '\n')
                    if material.young   != 0.0: file.write(f'material{i + 1}.young = {material.young}' + '\n')
                    if material.poisson != 0.0: file.write(f'material{i + 1}.poisson = {material.poisson}' + '\n')
                    if material.density != 0.0: file.write(f'material{i + 1}.density = {material.density}' + '\n')
                    file.write('\n')
            # sections
            if len(modelDatabase.sections) > 0:
                file.write(separator + '\n')
                file.write(comment + 'SECTIONS' + '\n')
                file.write(separator + '\n')
                for i, section in enumerate(modelDatabase.sections.dataObjects()):
                    section = cast(Section, section)
                    file.write(f'section{i + 1} = modelDatabase.sections.new()' + '\n')
                    file.write(f"section{i + 1}.name = '{section.name}'" + '\n')
                    if section.elementSetName != '<Undefined>':
                        file.write(f"section{i + 1}.elementSetName = '{section.elementSetName}'" + '\n')
                    if section.materialName != '<Undefined>':
                        file.write(f"section{i + 1}.materialName = '{section.materialName}'" + '\n')
                    if section.stressState != '<Undefined>':
                        file.write(f"section{i + 1}.stressState = '{section.stressState}'" + '\n')
                    if section.planeThickness != 0.0:
                        file.write(f'section{i + 1}.planeThickness = {section.planeThickness}' + '\n')
                    file.write('\n')
            # concentrated loads
            if len(modelDatabase.concentratedLoads) > 0:
                file.write(separator + '\n')
                file.write(comment + 'CONCENTRATED LOADS' + '\n')
                file.write(separator + '\n')
                for i, concentratedLoad in enumerate(modelDatabase.concentratedLoads.dataObjects()):
                    concentratedLoad = cast(ConcentratedLoad, concentratedLoad)
                    file.write(f'concentratedLoad{i + 1} = modelDatabase.concentratedLoads.new()' + '\n')
                    file.write(f"concentratedLoad{i + 1}.name = '{concentratedLoad.name}'" + '\n')
                    if concentratedLoad.nodeSetName != '<Undefined>':
                        file.write(f"concentratedLoad{i + 1}.nodeSetName = '{concentratedLoad.nodeSetName}'" + '\n')
                    if concentratedLoad.x != 0.0: file.write(f'concentratedLoad{i + 1}.x = {concentratedLoad.x}' + '\n')
                    if concentratedLoad.y != 0.0: file.write(f'concentratedLoad{i + 1}.y = {concentratedLoad.y}' + '\n')
                    if concentratedLoad.z != 0.0: file.write(f'concentratedLoad{i + 1}.z = {concentratedLoad.z}' + '\n')
                    file.write('\n')
            # boundary conditions
            if len(modelDatabase.boundaryConditions) > 0:
                file.write(separator + '\n')
                file.write(comment + 'BOUNDARY CONDITIONS' + '\n')
                file.write(separator + '\n')
                for i, boundaryCondition in enumerate(modelDatabase.boundaryConditions.dataObjects()):
                    boundaryCondition = cast(BoundaryCondition, boundaryCondition)
                    file.write(f'boundaryCondition{i + 1} = modelDatabase.boundaryConditions.new()' + '\n')
                    file.write(f"boundaryCondition{i + 1}.name = '{boundaryCondition.name}'" + '\n')
                    if boundaryCondition.nodeSetName != '<Undefined>':
                        file.write(f"boundaryCondition{i + 1}.nodeSetName = '{boundaryCondition.nodeSetName}'" + '\n')
                    if boundaryCondition.x != 0.0:
                        file.write(f'boundaryCondition{i + 1}.x = {boundaryCondition.x}' + '\n')
                    if boundaryCondition.y != 0.0:
                        file.write(f'boundaryCondition{i + 1}.y = {boundaryCondition.y}' + '\n')
                    if boundaryCondition.z != 0.0:
                        file.write(f'boundaryCondition{i + 1}.z = {boundaryCondition.z}' + '\n')
                    if boundaryCondition.isActiveInX:
                        file.write(f'boundaryCondition{i + 1}.isActiveInX = {boundaryCondition.isActiveInX}' + '\n')
                    if boundaryCondition.isActiveInY:
                        file.write(f'boundaryCondition{i + 1}.isActiveInY = {boundaryCondition.isActiveInY}' + '\n')
                    if boundaryCondition.isActiveInZ:
                        file.write(f'boundaryCondition{i + 1}.isActiveInZ = {boundaryCondition.isActiveInZ}' + '\n')
                    file.write('\n')

    # attribute slots
    __slots__ = ()
