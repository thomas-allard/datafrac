Welcome lol

#Files
Folders
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
