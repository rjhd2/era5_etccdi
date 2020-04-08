#!/usr/bin/python
#*******************************************
# START
#*******************************************
import os
import datetime as dt
import calendar
import iris
import numpy as np
import sys
import time

import utils

sys.path.append('/data/users/rdunn/reanalyses/code/era5/cdsapi-0.1.4')
import cdsapi

"""
Butchered from 

http://fcm1.metoffice.com/projects/utils/browser/CM_ML/trunk/NAO_Precip_Regr/get_era5_uwind.py

"""

#****************************************
def check_success(year, month, variable):
    '''
    Check that this cube has been downloaded successfully
    '''

    if not os.path.exists(os.path.join(utils.DATALOC, "{}{:02d}_hourly_{}.nc".format(year, month, variable))):
        return False

    cubelist = iris.load(os.path.join(utils.DATALOC, "{}{:02d}_hourly_{}.nc".format(year, month, variable)))

    cube = cubelist[0]

    if len(np.unique(cube.data[-1,:,:])) == 1:
        # single value for all the final hour of the data, download likely to be unsuccessful
        return False
    else:
        return True # check_success

#****************************************
def retrieve(year, month, variable, ndays):
    '''
    Use ECMWF API to get the data

    4.5GB per month --> 55GB per year, 50mins per month of processing
    '''

    if variable == "2m_temperature":
        varlist = ["2m_temperature", "land_sea_mask"]
    elif variable == "total_precipitation":
        varlist = ["total_precipitation"]
    else:
        print("please provide correct variable to download")
        return
    
    days = ["{:2d}".format(d+1) for d in range(ndays)]

    c = cdsapi.Client()

    c.retrieve(
        'reanalysis-era5-single-levels',
        {
            'product_type':'reanalysis',
            'format':'netcdf',
            'variable':varlist,
            'year':"{}".format(year),
            'month':"{:02d}".format(month),
            'day':days,
            'time':[
                '00:00','01:00','02:00',
                '03:00','04:00','05:00',
                '06:00','07:00','08:00',
                '09:00','10:00','11:00',
                '12:00','13:00','14:00',
                '15:00','16:00','17:00',
                '18:00','19:00','20:00',
                '21:00','22:00','23:00',
            ]
        },
        os.path.join(utils.DATALOC, "{}{:02d}_hourly_{}.nc".format(year, month, variable))
        )

    time.sleep(5) # to allow any writing process to finish up.

    # make a "success" file
    with open(os.path.join(utils.DATALOC, "{}{:02d}_{}_success.txt".format(year, month, variable)), "w") as outfile:
        
        outfile.write("Success {}".format(dt.datetime.now()))

    return # retreive

#****************************************
def combine(year, month, remove=False):
    """
    Now need to merge files for T and P
      Overlap of delayed and 5-day ERA5 - hence can given as tp_0001 and tp_0005 fields
      https://confluence.ecmwf.int/pages/viewpage.action?pageId=171414041
    
    Though won't be for most fields
    """

    # aim to add the precipitation cube to the temperature one.  Read both in
    variable = "2m_temperature"
    cubelist = iris.load(os.path.join(utils.DATALOC, "{}{:02d}_hourly_{}.nc".format(year, month, variable)))

    variable = "total_precipitation"
    p_cubelist = iris.load(os.path.join(utils.DATALOC, "{}{:02d}_hourly_{}.nc".format(year, month, variable)))

    # if it contains 2 cubes
    if len(p_cubelist) == 2:
        # extract both cubes
        pcube1 = p_cubelist[0]
        pcube2 = p_cubelist[1]

        masked1, = np.where(pcube1.data.mask[:, 0, 0] == True)
        masked2, = np.where(pcube2.data.mask[:, 0, 0] == True)

        # use locations of masks to overwrite
        tp_cube = pcube1[:]
        tp_cube.data[masked1] = pcube2.data[masked1]
        tp_cube.var_name = "tp"

    # else it's just a single cube, so easier to deal with
    elif len(p_cubelist) == 1:

        tp_cube = p_cubelist[0]
        tp_cube.var_name = "tp"


    # append precipitation cube to temperature one
    cubelist += [tp_cube]

    # and write out (6GB so takes a while!)
    iris.save(cubelist, os.path.join(utils.DATALOC, "{}{:02d}_hourly.nc".format(year, month)), zlib=True)

    # make success file 
    with open(os.path.join(utils.DATALOC, "{}{:02d}_success.txt".format(year, month)), "w") as outfile:
                outfile.write("Success {}".format(dt.datetime.now()))

    # remove input files
    if remove:
        for variable in ["2m_temperature", "total_precipitation"]:
            os.remove(os.path.join(utils.DATALOC, "{}{:02d}_hourly_{}.nc".format(year, month, variable)))

    return # combine
    
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

        if os.path.exists(os.path.join(utils.DATALOC, "{}_daily.nc".format(year))):
            print("{} - already downloaded and processed".format(year))
        else:
            for month in np.arange(1, 13):

                print("{} - {}".format(year, month))
                # get number of days
                ndays = calendar.monthrange(year, month)[1]
                
                if dt.datetime.now() > dt.datetime(year, month, 1):

                    if not os.path.exists(os.path.join(utils.DATALOC, "{}{:02d}_success.txt".format(year, month))):

                        for variable in ["2m_temperature", "total_precipitation"]:

                            if not os.path.exists(os.path.join(utils.DATALOC, "{}{:02d}_hourly_{}.nc".format(year, month, variable))):
                                while not check_success(year, month, variable):
                                    retrieve(year, month, variable, ndays)
                            else:
                                # check if success file exists.
                                if not os.path.exists(os.path.join(utils.DATALOC, "{}{:02d}_{}_success.txt".format(year, month, variable))):
                                    os.remove(os.path.join(utils.DATALOC, "{}{:02d}_hourly_{}.nc".format(year, month, variable)))
                                    while not check_success(year, month, variable):
                                        retrieve(year, month, variable, ndays)
                                else:
                                    print("{} - {} - {} already downloaded".format(year, month, variable))    


                        combine(year, month, remove = args.remove)

                    else:
                        print("{} - {} already downloaded".format(year, month))    
                        
                else:
                    print("{} - {} in future - not getting data".format(year, month))
#*******************************************
# END
#*******************************************
