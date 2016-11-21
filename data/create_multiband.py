__author__ = 'scottsfarley'

import os



for month in range(1, 13):
    outfile = "merged/prcp_" +str(month) + "_merge.tiff"
    cmd = "gdal_merge.py -o " + outfile + " -separate "
    for year in range(0, 23000, 1000):
        infile = "snapshot/prcp_" + str(month) + "_" + str(year) + ".tif "
        cmd += infile
    os.system(cmd)