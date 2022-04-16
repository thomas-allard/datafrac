import os
import time
import numpy as np
import abaqusConstants
from odbAccess import *
import array

#================================================================ PARAMETERS ===
number_of_nodes = 2760  # don't change unless mesh is changed

option = 2          # 1 for elastic only
                    # 2 for xfem
                    
#====================================================================== MAIN ===
# define some parameters based on option 1 or 2
if option == 1:
    directory = 'final_elastic/'
    filename = 'tension_elastic_job.odb'
    end_frame = 81
elif option == 2:
    directory = 'final_fracture/'
    filename = 'tension_fracture_job.odb'
    end_frame = 290
else:
    print('Specify a valid option! :0')

# open odb
odb = openOdb(path=directory+filename)

# define some variables to store nodes
all = odb.rootAssembly.instances['PLATE_1'].\
    nodeSets['ALL']
    
nodes = odb.rootAssembly.instances['PLATE_1'].\
    nodes[:]

# stack frames into a list to iterate through 
start_frame = 0
frames = []
for i in range(start_frame,end_frame):
    frames.append(odb.steps['Static'].frames[i])
    
    
# create a list of node Ids
nodeIds = [int(i) for i in range(1, number_of_nodes + 1)]


# loop through frames
for t in frames:
    time = t.frameValue
    Id = t.frameId
    strId = str(Id)

    string = 'frame # ' + str(Id) + ' at time: ' + str(time) + '\n'
    
    # extract displacements
    disps = t.fieldOutputs['U']
    displacementss = disps.getSubset(region=all)
    Ux, Uy = [], []
    for v in displacementss.values:
        '''
        Recycle the commented stuff below for when we extract nodal coordinates
        '''
        #us = '(' + str(ux) + ',' + str(uy) + ')'
        #label = v.nodeLabel
        #print('\tNode' + str(label) + ' disps = ' + us)
        # coords = all[v.nodeLabel].coordinates[:]
        # x, y = coords[0], coords[1]
        # pos = '(' + str(x) + ',' + str(y) + ')'
        ux, uy = v.data[0], v.data[1]
        Ux.append(ux)
        Uy.append(uy)

        
    # extract stresses
    stress = t.fieldOutputs['S']
    stresses = stress.getSubset(region=all)
    mises = []
    s11, s22, s12 = [], [], []
    for v in stresses.values:
        mises.append(v.mises)
        s11.append(v.data[0])
        s22.append(v.data[1])
        s12.append(v.data[3])
    
    # extract strains
    strain = t.fieldOutputs['NE']
    strains = strain.getSubset(region=all)
    NE11, NE22, NE12 = [], [], []
    for v in strains.values:
        NE11.append(v.data[0])
        NE22.append(v.data[1])
        NE12.append(v.data[3])
    
    # write text file for current frame
    block = np.vstack([Ux, Uy, mises, s11, s22, s12, NE11, NE22, NE12])
    out_name = directory + 'step_' + strId.zfill(3) +'.txt'
    np.savetxt(out_name,np.transpose(block))
    
    # append timing information at the end of the file
    with open(out_name,'a') as f:
        #f.write('\n' + str(time))
        f.write(str(time))
    
odb.close()