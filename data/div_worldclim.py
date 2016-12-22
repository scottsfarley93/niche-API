__author__ = 'scottsfarley'


import os

basefolder = "/users/scottsfarley/downloads/tmin_5m_bil/"
outfolder = basefolder + "/div/"

for i in range (1, 13):
    filename = "tmin" + str(i) + ".bil"
    outfile = outfolder + filename
    cmd = "gdal_calc.py -A " + basefolder + filename + " --outfile=" + outfile + " --calc=A/10"
    os.system(cmd)
