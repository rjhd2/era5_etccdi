#!/bin/env python
"""
Merge the individual tiles together for a given ETCCDI index

Run as::

  python merge_tiles.py --index TX90p

--index     ETCCDI index to process
"""

#*******************************************
# START
#*******************************************
import os
import glob
import calendar
import numpy as np

import iris
from iris.util import equalise_attributes
import iris.coord_categorisation
import netCDF4 as ncdf

import utils

#****************************************
def merge_cubes(index, timescale):
    '''
    Find all the files which should be part of the cube and merge into a single list
    '''

    files = []
    print("finding files")
    path = os.path.join(utils.DATALOC, "indices", "{}_{}_climpact.era5_historical_*_{}-{}.nc".format(index.lower(), timescale.upper(), utils.base_period_start, utils.base_period_end))
    print(path)
    files = glob.glob(path)
    
    print("loading {} files".format(len(files)))

    if len(files) > 0:
        cubelist = iris.load(files)
        equalise_attributes(cubelist)
        
        # and merge the cubes
        merged_cubes = cubelist.concatenate()
        
        assert len(merged_cubes) == 1

        return merged_cubes[0]
    else:
        return np.array([]) # merge_cubes

#****************************************
def remove_coords(cube, monthly = True):
    '''
    Remove time bounds and added Auxillary coordinate of months
    '''

    cube.coord("time").bounds = None

    if monthly:
        cube.remove_coord("month") 

    return cube # remove_coords

#****************************************
def main(index, lsm_year):
    '''
    Combine cubes for annual and monthly into single output file.
    '''

    if not os.path.exists(os.path.join(utils.DATALOC, "final")):
        os.mkdir(os.path.join(utils.DATALOC, "final"))


    # get annual cube
    annual_cube = merge_cubes(index, "ann")
    # if no files

    if annual_cube.shape[0] == 0:

        if "spei" in index.lower() or "spi" in index.lower():
            # these don't have annual versions
            pass
        else:            
            print("No files found")
            return

    if "spei" in index.lower() or "spi" in index.lower():
        final_cubelist = []
    else:
        annual_cube.var_name = "Ann"
        annual_cube = remove_coords(annual_cube, monthly = False)
        annual_cube.data.fill_value = utils.MDI
        annual_cube.missing_value = utils.MDI
        annual_cube._FillValue = utils.MDI
   
        final_cubelist = [annual_cube]

    if index in ["TN10p", "TN90p", "TX10p", "TX90p", "TNn", "TNx", "TXn", "TXx", "DTR", "Rx1day", "Rx5day", \
                 "TMm", "TXm", "TNm", "TXge35", "TXge30", "TMlt10", "TMge10", "TMlt5", "TMge5", "TXgt50p", \
                 "TNlt2", "TNltm2", "TNltm20", "Rx3day", "3month_SPEI", "6month_SPEI", "12month_SPEI", \
                 "3month_SPI", "6month_SPI", "12month_SPI"]:
        # get monthly cube
        monthly_cube = merge_cubes(index, "mon")

        # now process cube into months
        iris.coord_categorisation.add_month(monthly_cube, 'time', name='month')

        # extract each month
        for m in calendar.month_abbr:
            if m == "":
                continue
            else:
                print(m)
                monthConstraint = iris.Constraint(month=m)

                month_cube = monthly_cube.extract(monthConstraint)
                month_cube.var_name = m
                month_cube = remove_coords(month_cube)               
                
                month_cube.data.fill_value = utils.MDI
                month_cube.missing_value = utils.MDI
                month_cube._FillValue = utils.MDI

                final_cubelist += [month_cube]

    # and save the list
    iris.save(final_cubelist, os.path.join(utils.DATALOC, "final", "ERA5_{}_{}-{}.nc".format(index, utils.STARTYEAR, utils.ENDYEAR)), fill_value=utils.MDI, zlib=True)

    # apply land_sea mask
    lsm_cube = iris.load_cube(os.path.join(utils.DATALOC, "hourlies", "{}{:02d}_hourly.nc".format(lsm_year, 1)), "land_binary_mask")

    for cube in final_cubelist:
        lsm_data = lsm_cube.data[:cube.shape[0]]
        cube.data[lsm_data < utils.LAND_FRACTION_THRESH] = utils.MDI
        cube.data = np.ma.masked_where(lsm_data < utils.LAND_FRACTION_THRESH, cube.data)
        cube.data.fill_value = utils.MDI

    iris.save(final_cubelist, os.path.join(utils.DATALOC, "final", "ERA5_{}_{}-{}_land.nc".format(index, utils.STARTYEAR, utils.ENDYEAR)), fill_value=utils.MDI, zlib=True)

    return # main


#****************************************
if __name__ == "__main__":

    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', dest='index', action='store', default="TX90p", 
                        help='etccdi index')
    parser.add_argument('--lsm_year', dest='lsm_year', action='store', default="2020", 
                        help='Year to find file with LSM information (YYYY01_hourly.nc)')

    args = parser.parse_args()

    if args.index in ["ETR", "R99pTOT", "R95pTOT"]:
        print("merging not required for {}".format(args.index))
    else:
        main(args.index, args.lsm_year)
         
#*******************************************
# END
#*******************************************
