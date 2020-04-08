#!/bin/env python
#
#  Calculate the 3 missing indices
#
#
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
def get_cubelists(name1, name2):
    """
    Read in the two cube lists required for calculations

    :param str name1: first name
    :param str name2: second name

    :returns: cubelist1, cubelist2
    """


    path = os.path.join(utils.DATALOC, "final", "ERA5_{}_1979-{}.nc".format(name1, utils.ENDYEAR))
    print(path)
    cubelist1 = iris.load(path)

    path = os.path.join(utils.DATALOC, "final", "ERA5_{}_1979-{}.nc".format(name2, utils.ENDYEAR))
    print(path)
    cubelist2 = iris.load(path)

    return cubelist1, cubelist2 # get_cubelists


#****************************************
def RXXpTOT(index="R95pTOT"):
    """
    Calculates the R95pTOT/R99pTOT from R95p/R99p and PRCPTOT

    :param str index: which of R95pTOT or R99pTOT to calulate
    """

    descriptor = {"R95pTOT" : "very", "R99pTOT" : "extremely"}

    if index == "R95pTOT":
        rXXp, prcptot = get_cubelists("R95p", "PRCPTOT")

    elif index == "R99pTOT":
        rXXp, prcptot = get_cubelists("R99p", "PRCPTOT")

    rXXp_names = [c.var_name for c in rXXp]
    prcptot_names = [c.var_name for c in prcptot]

    rxxptot_list = []
    for name in rXXp_names:

        rxxptot_cube = 100 * rXXp[rXXp_names.index(name)] / prcptot[prcptot_names.index(name)]
        rxxptot_cube.name = "Contribution from {} wet days".format(descriptor[index])
        rxxptot_cube.var_name = name

        rxxptot_list += [rxxptot_cube]

    iris.save(rxxptot_list, os.path.join(utils.DATALOC, "indices", "ERA5_{}_1979-{}.nc".format(index, utils.ENDYEAR)), fill_value=utils.MDI, zlib=True)

    return # RXXpTOT


#****************************************
def etr():
    """
    Calculates the ETR
    """

    txx, tnn = get_cubelists("TXx", "TNn")

    txx_names = [c.var_name for c in txx]
    tnn_names = [c.var_name for c in tnn]

    etr_list = []
    for name in txx_names:

        etr_cube = txx[txx_names.index(name)]-tnn[tnn_names.index(name)]
        etr_cube.name = "Extreme Temperature Range"
        etr_cube.var_name = name

        etr_list += [etr_cube]

    iris.save(etr_list, os.path.join(utils.DATALOC, "indices", "ERA5_ETR_1979-{}.nc".format(utils.ENDYEAR)), fill_value=utils.MDI, zlib=True)

    return # etr


#****************************************
def main(index):
    '''
    Calls correct routine for specified index

    :param str index: which index to run (ETR/R95pTOT/R99pTOT)
    '''

    if index == "ETR":
        etr()

    elif index == "R95pTOT":
        RXXpTOT(index)

    elif index == "R99pTOT":
        RXXpTOT(index)

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
