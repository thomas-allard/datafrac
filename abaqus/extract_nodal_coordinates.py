import os
import time
import numpy as np
import array

#================================================================ PARAMETERS ===
option = 2          # 1 for elastic only
                    # 2 for xfem
                    
#====================================================================== MAIN ===
# define some parameters based on option 1 or 2
if option == 1:
    directory = 'final_elastic/'
    filename = 'tension_elastic_job.inp'
elif option == 2:
    directory = 'final_fracture/'
    filename = 'tension_fracture_job.inp'
else:
    print('Specify a valid option! :0')
    
# read in file contents
file = directory+filename
with open(file, 'r') as f:
    input_content = np.asarray(f.read().splitlines())
    
lines = []
node_indices = []
element_indices = []

# find lines corresponding to nodes and elements
for index, text in enumerate(input_content):
    lines.append(text)
    if "*Node" in text:
        node_indices.append(index)
    if "*Element" in text:
        element_indices.append(index)
        
# store relevant info
node_ids, nX, nY = [], [], []
start = node_indices[0]+1
stop = element_indices[0]
for j, row in enumerate(lines[start:stop]):
    text = row.split(',')
    node_id = int(text[0])
    x, y = float(text[1]), float(text[2])
    
    node_ids.append(node_id)
    nX.append(x)
    nY.append(y)

# write text file for nodes
node_block = np.vstack([node_ids, nX, nY])
out_name = f'{directory}nodes.txt'
np.savetxt(out_name, np.transpose(node_block))