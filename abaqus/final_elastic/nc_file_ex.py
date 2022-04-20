import netCDF4
import numpy as np
import os

# load data
fname = 'elastic_cdf.nc' # change for filename to use
nc = netCDF4.Dataset(fname)
save_file = False

# here are some examples
print(nc)
print(nc.variables['step_080'].time)
print(nc.variables['step_080'][:].data)
print(np.shape(nc.variables['step_080'][:].data))
