#!/bin/env python
"""
Utility routines and settings of these codes
"""


import os
import numpy as np

DATALOC = "/scratch/rdunn/reanalyses/era5"

DELTALAT = 8
DELTALON = 8

box_edge_lons = np.arange(0, 360 + DELTALON, DELTALON)
box_edge_lats = np.arange(-90, 90 + DELTALAT, DELTALAT)

MDI = -99.9

base_period_start = 1961
base_period_end = 1990

STARTYEAR = 1940
ENDYEAR = 2023

LAND_FRACTION_THRESH = 0.6

for newdir in ["raw", "hourlies", "dailies", "indices", "tiles", "final"]:
    if not os.path.exists(os.path.join(DATALOC, newdir)):
        os.mkdir(os.path.join(DATALOC, newdir))

#****************************************
def chunks(l, n):
    """ Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i: i+n]
