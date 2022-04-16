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
'''
#================================================================ PARAMETERS ===
number_of_nodes = 2760  # don't change unless mesh is changed

option = 1          # 1 for elastic only
                    # 2 for xfem
#================================================================= FUNCTIONS ===
def file2array(file, range, split=' '):
    # load in each line of data as array
    with open(file, 'r') as f:
        line_string = f.read().splitlines()
    list = []
    
    for i, line in enumerate(line_string):
        if i < range: 
            list.append(line.split(split))
        if i == range:
            thing = line.split(split)
            timestamp = thing
    #print(list)
    array = np.asarray(list, dtype=np.float64)
    #array = np.asarray(list)
    return(array, timestamp)

def createDataArray(file, range):
    #col_labels = ['node', 'ux', 'uy']
    dim = ('node', 'fields')
    #label = {'node':['nodeID'],'fields':['ux (mm)','uy (mm)']}
    label = {'fields':['ux','uy','Mises','S11','S22','S12','NE11','NE22','NE12']}
    array, timestamp = file2array(file, range)
    print(np.shape(array))
    #ux = array[:,0]
    #uy = array[:,1]
    #dataset = xr.DataArray(array, coords=col_labels, attrs={timestamp})
    dataset = xr.DataArray(array, dims=dim, coords=label, attrs={'time':timestamp})
    return(dataset)

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
print(f'Number of .txt files found = {len(files)}')
#print(files)

# read in text files and stack into a dictionary
datasets = {}
for file in files:
    name = file[:-4]
    dataArray = createDataArray(file, number_of_nodes)
    datasets[name] = dataArray

# combine DataArrays into a dataset    
set = xr.Dataset(datasets)

# Output DataSet as CDF file
set.to_netcdf(outname)

# switch back to original directory
os.chdir(cwd)
# if __name__ == '__main__':
    # main()