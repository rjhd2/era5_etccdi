#!/bin/env python
"""
Split up the annual files of daily data into tiles of daily values over the whole record

Run as::

  python make_files.py --batch N --total M

--batch    ID of the tile 
--total    Total number of tiles
"""

#*******************************************
# START
#*******************************************
import os
import fnmatch
import datetime
import numpy as np

import iris
import iris.coord_categorisation
import cf_units
import netCDF4 as ncdf

import utils

#****************************************
def find_files():
    '''
    Find all the files which should be part of the cube
    '''

    files = []
    for filename in os.listdir(utils.DATALOC):
        if fnmatch.fnmatch(filename, '????_daily.nc'):
            files += [os.path.join(utils.DATALOC, filename)]

    return files # find_files

#****************************************
def latConstraint(lats):
    return iris.Constraint(latitude = lambda cell: lats[0] <= cell < lats[1])

#****************************************
def lonConstraint(lons):
    return iris.Constraint(longitude = lambda cell: lons[0] <= cell < lons[1])

#****************************************
def main(tile_ids):
    '''
    Spin through Latitudes and Longitudes to extract tiles for Climpact
    '''
        
    if not os.path.exists(os.path.join(utils.DATALOC, "tiles")):
        os.mkdir(os.path.join(utils.DATALOC, "tiles"))


    files = find_files()

    cubelist = iris.load(files)

    new_list = cubelist.concatenate()

    # have to use a counter method to assign lats/lons to tile numbers
    tile = 1
    for t, lat in enumerate(utils.box_edge_lats):
        if t == 0: continue
        for n, lon in enumerate(utils.box_edge_lons):
            if n == 0: continue

            # if tile not selected in this batch
            if tile < tile_ids[0] or tile > tile_ids[-1]:
                pass
            else:
                print("lat {}, lon {}".format(t, n))

                # in case it has already been processed
                if os.path.exists(os.path.join(utils.DATALOC, "tiles", "era5_tile_{}.nc".format(tile))):
                    print("    already processed")

                else:
                    # coordinate constraints
                    lat_constraint = latConstraint([utils.box_edge_lats[t-1], lat])
                    lon_constraint = lonConstraint([utils.box_edge_lons[n-1], lon])

                    tile_list = []
                    # apply to all variables
                    for cube in new_list:
                        print(cube.var_name)

                        tile_cube = cube.extract(lat_constraint)
                        tile_cube = tile_cube.extract(lon_constraint)

                        # fix units for Climpact
                        if tile_cube.var_name == "tp":
                            tile_cube.units = cf_units.Unit("kg m-2 d-1")
                        # fix missing data in lots of ways

                        try:
                            if tile_cube.data.mask == False:
                                tile_cube.data.mask = np.zeros(tile_cube.shape)
                            elif tile_cube.data.mask == False:
                                tile_cube.data.mask = np.ones(tile_cube.shape)
                        except ValueError:
                            # have a proper array
                            pass

                        tile_cube.data[tile_cube.data.mask == True] = utils.MDI

                        tile_cube.data.fill_value = utils.MDI
                        tile_cube._FillValue = utils.MDI
                        tile_cube.missing_value = utils.MDI

                        tile_list += [tile_cube]

                    # save file
#                    print("era_tile_{}.nc".format(tile))
#                    input("stop")
                    iris.save(tile_list, os.path.join(utils.DATALOC, "tiles", "era5_tile_{}.nc".format(tile)), fill_value=utils.MDI, zlib=True)

                    # use ncdf library to force setting of keywords
                    ncfile = ncdf.Dataset(os.path.join(utils.DATALOC, "tiles", "era5_tile_{}.nc".format(tile)), 'r+')

                    for var in ["tx2m", "tn2m", "tp"]:

                        ncfile.variables[var].missing_value = utils.MDI
                        ncfile.variables[var].fill_value = utils.MDI

                    ncfile.close()

                    print("       done")
            tile += 1

    return # main

#****************************************
if __name__ == "__main__":

    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--batch', dest='batch', action='store', default=0, type=int,
                        help='batch number')
    parser.add_argument('--total', dest='total', action='store', default=100, type=int,
                        help='total number of batches')

    args = parser.parse_args()

    # set up the number of parallel tiles to run

    n_tiles = (len(utils.box_edge_lats)-1) * (len(utils.box_edge_lons)-1)

    batch_size = np.ceil(n_tiles / args.total).astype(int)

    tiles_to_run = list(utils.chunks(np.arange(1, n_tiles+1), batch_size))

    print("Batch {} of {}".format(args.batch, args.total))
    try:
        main(tiles_to_run[args.batch])
    except IndexError:
        # account for rounding and imperfect division
        pass

#*******************************************
# END
#*******************************************
