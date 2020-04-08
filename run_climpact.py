#!/bin/env python
#
#  Convert annual files into tiles of complete record
#
#
#*******************************************
# START
#*******************************************
import os
import datetime
import numpy as np
import subprocess

import utils


#******************************************************************************************
#******************************************************************************************
class cd:
    """
    Context manager for changing the current working directory

    https://stackoverflow.com/questions/431684/how-do-i-cd-in-python/13197763#13197763
    """
    def __init__(self, newPath):
        self.newPath = os.path.expanduser(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


#******************************************************************************************
def main(tile_ids):
    """
    Run the Climpact2 code on the tile

    change directory to the Climpact 2 code, make the new wrapper and run it

    :param int tile: tile to process

    """ 

    # set relative to current as checked out as part of the repository
    CLIMPACT_LOCS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "climpact2-master")

    # make sure output directory exists.
    if not os.path.exists(os.path.join(utils.DATALOC, "indices")):
        os.mkdir(os.path.join(utils.DATALOC, "indices"))

    for tile in tile_ids:
        # make sure it can run
        if not os.path.exists(os.path.join(utils.DATALOC, "tiles", "era5_tile_{}.nc".format(tile))):
            return

        try:
            # change directory to where code is
            with cd(CLIMPACT_LOCS):
                # make the new wrapper file
                wrapper = os.path.join(CLIMPACT_LOCS,  "climpact2.ncdf.wrapper.{}.r".format(tile))

                with open(wrapper, "w") as wrapperfile:

                    wrapperfile.write("# ------------------------------------------------\n")
                    wrapperfile.write("# This wrapper script calls the 'create.indices.from.files' function from the modified climdex.pcic.ncdf package\n")
                    wrapperfile.write("# to calculate ETCCDI, ET-SCI and other indices, using data and parameters provided by the user.\n")
                    wrapperfile.write("# Note even when using a threshold file, the base.range parameter must still be specified accurately.\n")
                    wrapperfile.write("# ------------------------------------------------\n")
                    wrapperfile.write("\n")
                    wrapperfile.write("library(climdex.pcic.ncdf)\n")
                    wrapperfile.write("# list of one to three input files. e.g. c(\"a.nc\",\"b.nc\",\"c.nc\")\n")
                    wrapperfile.write("infiles=\"{}\"\n".format(os.path.join(utils.DATALOC, "tiles", "era5_tile_{}.nc".format(tile))))
                    wrapperfile.write("\n")
                    wrapperfile.write("# list of variable names according to above file(s)\n")
                    wrapperfile.write("vars=c(prec=\"tp\",tmax=\"tx2m\", tmin=\"tn2m\")\n")
                    wrapperfile.write("\n")
                    wrapperfile.write("# output directory. Will be created if it does not exist.\n")
                    wrapperfile.write("outdir=\"{}\"\n".format(os.path.join(utils.DATALOC, "indices")))
                    wrapperfile.write("\n")
                    wrapperfile.write("# Output filename format. Must use CMIP5 filename convention. i.e. \"var_timeresolution_model_scenario_run_starttime-endtime.nc\"\n")
                    wrapperfile.write("file.template=\"var_daily_climpact.era5_historical_{}_{}-{}.nc\"\n".format(tile, utils.base_period_start, utils.base_period_end))
                    wrapperfile.write("\n")
                    wrapperfile.write("# author data\n")
                    wrapperfile.write("author.data=list(institution=\"Met Office Hadley Centre\", institution_id=\"MOHC\")\n")
                    wrapperfile.write("\n")
                    wrapperfile.write("# reference period\n")
                    wrapperfile.write("base.range=c({},{})\n".format(utils.base_period_start, utils.base_period_end))
                    wrapperfile.write("\n")
                    wrapperfile.write("# number of cores to use, or FALSE for single core.\n")
                    wrapperfile.write("cores=FALSE\n")
                    wrapperfile.write("\n")
                    wrapperfile.write("# list of indices to calculate, or NULL to calculate all.\n")
                    wrapperfile.write("indices=NULL	#c(\"hw\",\"tnn\")\n")
                    wrapperfile.write("\n")
                    wrapperfile.write("# input threshold file to use, or NULL for none.\n")
                    wrapperfile.write("thresholds.files=NULL#\"thresholds.test.1991-1997.nc\"\n")
                    wrapperfile.write("\n")
                    wrapperfile.write("#######################################################\n")
                    wrapperfile.write("# Esoterics below, do not modify without a good reason.\n")
                    wrapperfile.write("\n")
                    wrapperfile.write("# definition used for Excess Heat Factor (EHF). \"PA13\" for Perkins and Alexander (2013), this is the default. \"NF13\" for Nairn and Fawcett (2013).\n")
                    wrapperfile.write("EHF_DEF = \"PA13\"\n")
                    wrapperfile.write("\n")
                    wrapperfile.write("# axis to split data on. For chunking up of grid, leave this.\n")
                    wrapperfile.write("axis.name=\"Y\"\n")
                    wrapperfile.write("\n")
                    wrapperfile.write("# Number of data values to process at once. If you receive \"Error: rows.per.slice >= 1 is not TRUE\", try increasing this to 20. You might have a large grid.\n")
                    wrapperfile.write("maxvals=10\n")
                    wrapperfile.write("\n")
                    wrapperfile.write("# output compatible with FCLIMDEX. Leave this.\n")
                    wrapperfile.write("fclimdex.compatible=FALSE\n")
                    wrapperfile.write("\n")
                    wrapperfile.write("# Call the package.\n")
                    wrapperfile.write("create.indices.from.files(infiles,outdir,file.template,author.data,variable.name.map=vars,base.range=base.range,parallel=cores,axis.to.split.on=axis.name,climdex.vars.subset=indices,thresholds.files=thresholds.files,fclimdex.compatible=fclimdex.compatible,\n")
                    wrapperfile.write("	cluster.type=\"SOCK\",max.vals.millions=maxvals,\n")
                    wrapperfile.write("	thresholds.name.map=c(tx05thresh=\"tx05thresh\",tx10thresh=\"tx10thresh\", tx50thresh=\"tx50thresh\", tx90thresh=\"tx90thresh\",tx95thresh=\"tx95thresh\", \n")
                    wrapperfile.write("			tn05thresh=\"tn05thresh\",tn10thresh=\"tn10thresh\",tn50thresh=\"tn50thresh\",tn90thresh=\"tn90thresh\",tn95thresh=\"tn95thresh\",\n")
                    wrapperfile.write("			tx90thresh_15days=\"tx90thresh_15days\",tn90thresh_15days=\"tn90thresh_15days\",tavg90thresh_15days=\"tavg90thresh_15days\",\n")
                    wrapperfile.write("			tavg05thresh=\"tavg05thresh\",tavg95thresh=\"tavg95thresh\",\n")
                    wrapperfile.write("			txraw=\"txraw\",tnraw=\"tnraw\",precraw=\"precraw\", \n")
                    wrapperfile.write("			r95thresh=\"r95thresh\", r99thresh=\"r99thresh\"))\n")


                # close wrapper
                print(" ".join(["Rscript", wrapper]))
                subprocess.check_call(["Rscript", wrapper])
                os.remove(wrapper)

        except subprocess.CalledProcessError:
            # handle errors in the called executable
            raise Exception

        except OSError:
            # executable not found
            print("Cannot find Rscript")
            raise OSError

        print("...... done")

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
