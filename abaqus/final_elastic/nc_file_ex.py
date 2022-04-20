import netCDF4
import numpy as np
import os

# load data
fname = 'elastic_cdf.nc' # change for filename to use
nc = netCDF4.Dataset(fname)

# here are some examples
print(nc)
print(nc.variables['step_080'].time)
print(nc.variables['step_080'][:].data)
print(np.shape(nc.variables['step_080'][:].data))

# make a new array for time
time = []
print("Appending times to an np array")
for ii in range(len(nc.variables)-2):
    if ii < 10:
        print(nc.variables['step_00' + str(ii)].time)
        time.append(nc.variables['step_00' + str(ii)].time)
    elif ii >= 10 and ii < 100:
        print(nc.variables['step_0' + str(ii)].time)
        time.append(nc.variables['step_0' + str(ii)].time)
    else:
        print(nc.variables['step_' + str(ii)].time)
        time.append(nc.variables['step_' + str(ii)].time)
time = np.asarray(time)
print("Time:", time)
print("Shape of array:", np.shape(time))
