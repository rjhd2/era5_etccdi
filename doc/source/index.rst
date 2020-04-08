.. ERA5 ETCCDI documentation master file, created by
   sphinx-quickstart on Wed Apr  8 10:47:53 2020.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

ERA5 ETCCDI documentation
=========================

These are scripts to pull down the ERA5 reanalysis from ECMWF (and the
Climate Data Store), process and make ETCCDI indices.

Get ERA5
^^^^^^^^

Using the CDSAPI get the hourly T and P files for each month/year from the CDS.

https://cds.climate.copernicus.eu/cdsapp#!/dataset/reanalysis-era5-single-levels?tab=form

https://cds.climate.copernicus.eu/api-how-to

.. automodule:: get_era5
   :members: main

Convert ERA5
^^^^^^^^^^^^

Convert the files of hourly T and P for each month to annual files containing daily data.

.. automodule:: convert_era5
   :members: main

Make Tiles
^^^^^^^^^^

Make tiles to pass to Climpact as full resolution fields are too big
and this allows parallelisation

.. automodule:: make_tiles
   :members: main

Climpact2
^^^^^^^^^

Use Climpact2 (https://github.com/ARCCSS-extremes/climpact2) to calculate the ETCCDI indices for each tile

.. automodule:: run_climpact
   :members: main

Merge Tiles
^^^^^^^^^^^

Merge the tiles together for each index.

.. automodule:: merge_tiles
   :members: main

Extra Indices
^^^^^^^^^^^^^

Unfortunately not all indices are calculated by Climpact, so post
process to get ETR, R95pTOT and R99pTOT.

.. automodule:: extra_indices
   :members: main

Settings
^^^^^^^^
Settings are in the utils script



.. toctree::
   :maxdepth: 2
   :caption: Contents:



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
