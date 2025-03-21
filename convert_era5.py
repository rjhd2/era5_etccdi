#!/bin/env python
"""
Convert the monthly files of hourly T and P into annual files of daily values

Run as

  python convert_era5.py --start YEAR --end YEAR [--remove]

--remove    Remove the input monthly files at the end, leaving just daily files for each year
"""

#*******************************************
# START
#*******************************************
import os
import fnmatch
import datetime
import numpy as np
import datetime as dt

import iris
import iris.coord_categorisation
import cf_units

import utils

#****************************************
def make_dailies(year, month, remove = False):
    '''
    Convert hourly T and P fields into daily Tx, Tn and P-accumulations


    SPICE notes - 40GB, 10mins per year
    '''

    try:
        cubelist = iris.load(os.path.join(utils.DATALOC, "hourlies", "{}{:02d}_hourly.nc".format(year, month)))

        names = [str(c.var_name) for c in cubelist]

#        lsm = cubelist[names.index("lsm")]

        new_list = []
        for cube in cubelist:
#            if cube.var_name == "lsm":
#                continue
            print(cube.var_name)

            # mask all regions which are 100% ocean
#            cube.data[lsm.data == 0] = utils.MDI
#            cube.data = np.ma.masked_where(lsm.data == 0, cube.data)
#            cube.data.fill_value = utils.MDI

            # add a "day" indicator to allow aggregation
            iris.coord_categorisation.add_day_of_month(cube, "time", name="day_of_month")

            if cube.var_name == "tp":
                # precip
                p_cube = cube.aggregated_by(["day_of_month"], iris.analysis.SUM)
                p_cube.remove_coord("day_of_month")
                p_cube.data *= 1000. # convert to mm
                p_cube.units = "mm"

                # fix units for Climpact
                p_cube.units = cf_units.Unit("kg m-2 d-1")

                new_list += [p_cube]

            if cube.var_name == "t2m":
                # temperature
                cube.data -= 273.15 # convert to C
                cube.units = "degreesC"

                tx_cube = cube.aggregated_by(["day_of_month"], iris.analysis.MAX)
                tx_cube.remove_coord("day_of_month")
                tx_cube.var_name = "tx2m"
                tx_cube.long_name = "2 metre maximum temperature"

                tn_cube = cube.aggregated_by(["day_of_month"], iris.analysis.MIN)
                tn_cube.remove_coord("day_of_month")
                tn_cube.var_name = "tn2m"
                tn_cube.long_name = "2 metre minimum temperature"

                new_list += [tx_cube]
                new_list += [tn_cube]
        # end for cube in cubelist

        iris.save(new_list, os.path.join(utils.DATALOC, "dailies", "{}{:02d}_daily.nc".format(year, month)), zlib=True)

    except OSError:
        print("file missing")

    with open(os.path.join(utils.DATALOC, "{}{:02d}_daily_success.txt".format(year, month)), "w") as outfile:
        outfile.write("Success {}".format(dt.datetime.now()))

    print("{}-{} done".format(year, month))

    if remove:
        os.remove(os.path.join(utils.DATALOC, "hourlies", "{}{:02d}_hourly.nc".format(year, month)))
        
    return # make_dailies


#****************************************
def make_years(year, remove = False):
    '''
    Take all monthly files of daily values, and make a single year file
    Enables save at this point.
    '''

    files = []
    for filename in os.listdir(os.path.join(utils.DATALOC, "dailies")):
        if fnmatch.fnmatch(filename, '{}??_daily.nc'.format(year)):
            files += [os.path.join(utils.DATALOC, "dailies", filename)]

    assert len(files) == 12

    cubelist = iris.load(files)

    time_axis = 0            

    # "history" attribute prevents concatenation
    for cube in cubelist:
        del cube.attributes["history"]
        if cube.var_name == "tx2m":
            time_axis += cube.shape[0]

    new_list = cubelist.concatenate()

    # double check all cubes are merged
    for cube in new_list:
        assert cube.shape[0] == time_axis

    iris.save(new_list, os.path.join(utils.DATALOC, "dailies", "{}_daily.nc".format(year)), zlib=True)

    with open(os.path.join(utils.DATALOC, "{}_success.txt".format(year)), "w") as outfile:
        outfile.write("Success {}".format(dt.datetime.now()))

    if remove:
        for fn in files:
            os.remove(fn)

    return # make_years

#****************************************
if __name__ == "__main__":

    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--start', dest='start', action='store', default=1979, type=int,
                        help='Start year [1979]')
    parser.add_argument('--end', dest='end', action='store', default=2019, type=int,
                        help='End year [2019]')
    parser.add_argument('--remove', dest='remove', action='store_true', default=False,
                        help='Remove hourly and monthly files, default = False')

    args = parser.parse_args()         

    for year in np.arange(args.start, args.end+1):

        if os.path.exists(os.path.join(utils.DATALOC, "dailies", "{}_daily.nc".format(year))):
            print("{} - already downloaded and processed".format(year))
        else:
            for month in np.arange(1, 13):

                if not os.path.exists(os.path.join(utils.DATALOC, "dailies", "{}{:02d}_daily.nc".format(year, month))):
                    make_dailies(year, month, remove = args.remove)

            make_years(year, remove = args.remove)

#*******************************************
# END
#*******************************************
