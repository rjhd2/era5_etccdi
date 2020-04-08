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
from iris.experimental.equalise_cubes import equalise_attributes
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
    if timescale == "ann":

        path = os.path.join(utils.DATALOC, "indices", "{}ETCCDI_{}_climpact.era5_historical_*_{}-{}.nc".format(index.lower(), "yr", utils.base_period_start, utils.base_period_end))
        print(path)
        files = glob.glob(path)
    elif timescale == "mon":
        path = os.path.join(utils.DATALOC, "indices", "{}ETCCDI_{}_climpact.era5_historical_*_{}01-{}12.nc".format(index.lower(), "mon", utils.base_period_start, utils.base_period_end))
        print(path)
        files = glob.glob(path)
    
    print("loading {} files".format(len(files)))
    cubelist = iris.load(files)
    equalise_attributes(cubelist)

    # and merge the cubes
    merged_cubes = cubelist.concatenate()

    assert len(merged_cubes) == 1

    return merged_cubes[0] # merge_cubes

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
def main(index):
    '''
    Combine cubes for annual and monthly into single output file.
    '''

    if not os.path.exists(os.path.join(utils.DATALOC, "final")):
        os.mkdir(os.path.join(utils.DATALOC, "final"))


    # get annual cube
    annual_cube = merge_cubes(index, "ann")
    annual_cube.var_name = "Ann"
    annual_cube = remove_coords(annual_cube, monthly = False)
    annual_cube.data.fill_value = utils.MDI
    annual_cube.missing_value = utils.MDI
    annual_cube._FillValue = utils.MDI
   
    final_cubelist = [annual_cube]

    if index in ["TN10p", "TN90p", "TX10p", "TX90p", "TNn", "TNx", "TXn", "TXx", "DTR", "Rx1day", "Rx5day"]:
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
    iris.save(final_cubelist, os.path.join(utils.DATALOC, "final", "ERA5_{}_1979-{}.nc".format(index, utils.ENDYEAR)), fill_value=utils.MDI, zlib=True)

    return # main


#****************************************
if __name__ == "__main__":

    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', dest='index', action='store', default="TX90p", 
                        help='etccdi index')

    args = parser.parse_args()

    if args.index in ["ETR", "R99pTOT", "R95pTOT"]:
        print("merging not required for {}".format(args.index))
    else:
        main(args.index)
         
#*******************************************
# END
#*******************************************
