#!/bin/env python

"""
Post calculate extra ETCCDI indices which aren't done automatically by Climpact (ETR, R95pTOT, R99pTOT)

Run as::

  python extra_indices.py --index ETR

--index     ETCCDI indices to calculate (ETR, R95pTOT, R99pTOT)
"""

#*******************************************
# START
#*******************************************
import os
import glob
import calendar
import numpy as np

import iris
import iris.coord_categorisation
import netCDF4 as ncdf

import utils

#****************************************
def get_cubelists(name1, name2, land=False):
    """
    Read in the two cube lists required for calculations

    :param str name1: first name
    :param str name2: second name
    :param bool land: load on landmasked files

    :returns: cubelist1, cubelist2
    """

    if land:
        path = os.path.join(utils.DATALOC, "final", "ERA5_{}_{}-{}_land.nc".format(name1, utils.STARTYEAR, utils.ENDYEAR))
    else:
        path = os.path.join(utils.DATALOC, "final", "ERA5_{}_{}-{}.nc".format(name1, utils.STARTYEAR, utils.ENDYEAR))
    print(path)
    cubelist1 = iris.load(path)

    if land:
        path = os.path.join(utils.DATALOC, "final", "ERA5_{}_{}-{}_land.nc".format(name2, utils.STARTYEAR, utils.ENDYEAR))
    else:
        path = os.path.join(utils.DATALOC, "final", "ERA5_{}_{}-{}.nc".format(name2, utils.STARTYEAR, utils.ENDYEAR))
        
    print(path)
    cubelist2 = iris.load(path)

    return cubelist1, cubelist2 # get_cubelists


#****************************************
def RXXpTOT(index="R95pTOT", land=False):
    """
    Calculates the R95pTOT/R99pTOT from R95p/R99p and PRCPTOT

    :param str index: which of R95pTOT or R99pTOT to calulate
    :param bool land: load on landmasked files
    """

    descriptor = {"R95pTOT" : "very", "R99pTOT" : "extremely"}

    if index == "R95pTOT":
        rXXp, prcptot = get_cubelists("R95p", "PRCPTOT", land=land)

    elif index == "R99pTOT":
        rXXp, prcptot = get_cubelists("R99p", "PRCPTOT", land=land)

    rXXp_names = [c.var_name for c in rXXp]
    prcptot_names = [c.var_name for c in prcptot]

    rxxptot_list = []
    for name in rXXp_names:

        rxxptot_cube = 100 * rXXp[rXXp_names.index(name)] / prcptot[prcptot_names.index(name)]
        rxxptot_cube.name = "Contribution from {} wet days".format(descriptor[index])
        rxxptot_cube.var_name = name

        rxxptot_list += [rxxptot_cube]

    if land:
        iris.save(rxxptot_list, os.path.join(utils.DATALOC, "final", "ERA5_{}_{}-{}_land.nc".format(index, utils.STARTYEAR, utils.ENDYEAR)), fill_value=utils.MDI, zlib=True)
    else:
        iris.save(rxxptot_list, os.path.join(utils.DATALOC, "final", "ERA5_{}_{}-{}.nc".format(index, utils.STARTYEAR, utils.ENDYEAR)), fill_value=utils.MDI, zlib=True)

    return # RXXpTOT


#****************************************
def etr(land=False):
    """
    Calculates the ETR

    :param bool land: load on landmasked files
    """

    txx, tnn = get_cubelists("TXx", "TNn", land=land)

    txx_names = [c.var_name for c in txx]
    tnn_names = [c.var_name for c in tnn]

    etr_list = []
    for name in txx_names:

        etr_cube = txx[txx_names.index(name)]-tnn[tnn_names.index(name)]
        etr_cube.name = "Extreme Temperature Range"
        etr_cube.var_name = name

        etr_list += [etr_cube]
    
    if land:
        iris.save(etr_list, os.path.join(utils.DATALOC, "final", "ERA5_ETR_{}-{}_land.nc".format(utils.STARTYEAR, utils.ENDYEAR)), fill_value=utils.MDI, zlib=True)
    else:
        iris.save(etr_list, os.path.join(utils.DATALOC, "final", "ERA5_ETR_{}-{}.nc".format(utils.STARTYEAR, utils.ENDYEAR)), fill_value=utils.MDI, zlib=True)
    

    return # etr


#****************************************
def main(index):
    '''
    Calls correct routine for specified index

    :param str index: which index to run (ETR/R95pTOT/R99pTOT)
    '''

    if index == "ETR":
        etr()
        etr(land=True)

    elif index in ["R95pTOT", "R99pTOT"]:
        RXXpTOT(index)
        RXXpTOT(index, land=True)

    return # main


#****************************************
if __name__ == "__main__":

    import argparse

    # set up keyword arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', dest='index', action='store', default="TX90p", 
                        help='etccdi index')

    args = parser.parse_args()

    if args.index in ["R95pTOT", "R99pTOT", "ETR"]:

        main(args.index)

    else:
        print("no calculation necessary")
         
#*******************************************
# END
#*******************************************
