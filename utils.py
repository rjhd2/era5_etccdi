#!/bin/env python
"""
Utility routines and settings of these codes
"""


import os
import numpy as np

DATALOC = "/scratch/rdunn/reanalyses/era5"

DELTALAT = 10
DELTALON = 10

box_edge_lons = np.arange(0, 360 + DELTALON, DELTALON)
box_edge_lats = np.arange(-90, 90 + DELTALAT, DELTALAT)

MDI = -99.9

base_period_start = 1981
base_period_end = 2010

ENDYEAR = 2019

#****************************************
def chunks(l, n):
    """ Yield successive n-sized chunks from l."""
    for i in range(0, len(l), n):
        yield l[i: i+n]
