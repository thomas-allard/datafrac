import numpy as np 
import pandas as pd
import xarray as xr
import pickle
import glob, sys
import os

'''
---------------------- Summary of script as of 4/15/2022 -----------------------
This script compiles the step_{#}.txt files associated with an Abaqus output 
    database (ODB) which are extracted using "extract_results.py"

Data for each time step is stored in a DataArray.
A master DataSet is created by "stacking" all DataArrays for a simulations 
    corresponding to the entire duration of the simulation.
Each DataArray has a 2760 rows corresponding to the 2760 nodes of the mesh.
The following fields are the corresponding columns of each data array:
    - ux: displacement in the x-direction (mm). Nodal value
    - uy: displacement in the y-direction (mm). Nodal value
    - Mises: von Mises stress (MPa)
    - S11: normal stress component in the x-direction (MPa)
    - S22: normal stress component in the y-direction (MPa)
    - S12: shear stress component (MPa)
    - NE11: nominal normal strain in the x-direction (dimensionless)
    - NE22: nominal normal strain in the y-direction (dimensionless)
    - NE12: nominal shear strain (dimensionless)
    
Displacements, ux and uy, are nodal valued.
All stress and strain components are normally elemental quantities and are 
    calculated at the integration points. For the sake of this project, we 
    will keep all quantities at the nodes, so these values are calculated at
    the nodes. This operation is conducted automatically by Abaqus and are the 
    average stresses interpolated to the nodes. This operation is requested when
    building the simulation prior to submission in "build_model.py".
    
Currently, the DataSet is output as a NetCDF file, because it is easy. 
A saved DataSet may be loaded as follows:
    'set = xr.open_dataset('{filename}.nc')
    
Instructions for parsing out simulation data from the NetCDF file is forthcoming
    1. navigate to folder with relevant netcdf file and load. For example:
        import xarray as xr
        import numpy as np
        set = xr.open_dataset('elastic_cdf.nc')
    2. slice out a DataArray
        step_080 = set.step_080
    3. select a specific field
        ux_80 = step_080.sel(field='ux')
    4. convert to an array
        ux_80_array = ux_80.to_numpy()
'''
#================================================================ PARAMETERS ===
number_of_nodes = 2760  # don't change unless mesh is changed

option = 2          # 1 for elastic only
                    # 2 for xfem
#================================================================= FUNCTIONS ===
def file2array(file, range, split=' '):
    # load in each line of data as array
    with open(file, 'r') as f:
        line_string = f.read().splitlines()
    
    # loop through the lines from the file, split, and append to list
    list = []
    timestamp = 0 # default 
    for i, line in enumerate(line_string):
        # data lines
        if i < range: 
            list.append(line.split(split))
        # final line has the timestamp
        if i == range:
            thing = line.split(split)
            timestamp = thing

    # convert list to an array of type float64
    array = np.asarray(list, dtype=np.float64)

    return(array, timestamp)

def createDataArray(file, range, node_list):
    # call file2array to load in data
    array, timestamp = file2array(file, range)

    # define relevant information
    dim = ('node', 'field')
    field_labels = ['ux','uy','Mises','S11','S22','S12','NE11','NE22','NE12']
    labels = [("node",node_list), ("field",field_labels)]
    name = file[:-4]
    timestamp = str(timestamp)
    
    # create DataArray
    data = xr.DataArray(array, dims=dim, coords=labels, attrs={'time':timestamp}, name=name)
    
    return(data)

def collectNodes(file, range, node_list):
    # call file2array to load in data
    array, timestamp = file2array(file, range)
    
    # define relevant information
    dim = ('node', 'coordinate')
    coord_labels = ['id','x','y']
    labels = [("node",node_list), ("coordinate",coord_labels)]
    name = 'nodal_coordinates'
    
    # create DataArray
    data = xr.DataArray(array, dims=dim, coords=labels, name=name)
    
    return(data)

#====================================================================== MAIN ===
# define some parameters based on option 1 or 2
if option == 1:
    directory = 'final_elastic/'
    outname = 'elastic_cdf.nc'
    end_frame = 81
elif option == 2:
    directory = 'final_fracture/'
    outname = 'fracture_cdf.nc'
    end_frame = 290
else:
    print('Specify a valid option! :0')
    
# move around directories after checking it exists
cwd = os.getcwd()
newDir = f'{cwd}/{directory}'
isDir = os.path.isdir(newDir)
if isDir == True:
    os.chdir(newDir)
else:
    print('Not a valid directory! :0')

# grab text files
files = []
for file in glob.glob("*.txt"):
    files.append(file)
#files.remove(files.index('nodes.txt'))
files.remove('nodes.txt')
print(f'Number of .txt files found = {len(files)}')
#print(files)

# read in text files and stack into a dictionary
node_list = [str(i) for i in range(1,number_of_nodes+1)]
datasets = {}
for file in files:
    name = file[:-4]
    dataArray = createDataArray(file, number_of_nodes,node_list)
    datasets[name] = dataArray
    
# # get nodal coordaintes and add to dictionary
# NodeArray = collectNodes(file, number_of_nodes, node_list)
# datasets['nodal_coordinates'] = NodeArray

# combine DataArrays into a dataset    
set = xr.Dataset(datasets)

# Output DataSet as CDF file
set.to_netcdf(outname)

# switch back to original directory
os.chdir(cwd)
# if __name__ == '__main__':
    # main()