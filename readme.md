# Welcome lol

This project investigates the applicability of physics informed neural networks (PINN) for discovering material behavior parameters for two conditions:
1. elasticity
2. linear elastic fracture


#===============================================================================
## Files and folders
- abaqus/
    - final_elastic/
        - elastic_cdf.nc: Xarray DataSet saved as a netcdf. The main file we care about operating on!
        - Various extracted output files: step_000.txt through step_080.txt
        - Abaqus output files: tension_elastic_job.com, _.dat, _.inp, _.log, _.msg, _.odb, _.prt, and _.sta
    - final_fracture/ 
        - fracture_cdf.nc: Xarray DataSet saved as a netcdf. The main file we care about operating on!
        - Various extracted output files: step_000.txt through step_289.txt
        - Abaqus output files: tension_fracture_job.com, _.dat, _.inp, _.log, _.msg, _.odb, _.prt, and _.sta
    - build_model.py
    - extract_results.py
    - collect_results.py
- literature/
    - various pdf files
- old_PINNs/
    - NavierStokeExample.ipynb
    - cylinder_nektar_wake.mat
    - trained-navier-stokes.hdf5
    - trained-navier-stokes_bad.hdf5

#===============================================================================
## How to load a netcdf, indexing and slicing


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
