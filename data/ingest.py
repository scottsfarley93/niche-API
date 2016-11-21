import psycopg2
import os
import uuid
import subprocess



hostname = "144.92.235.14"
port = "5432"
user = "paleo"
p = "Alt0Sax!!"
database = "paleo"

source = 6
resolution = 0.5


try:
    connectString = "dbname='" + str(database) + "' user='" + str(user) + "' host='" + str(hostname) + "' password='" + str(p) + "'"
    conn = psycopg2.connect(connectString)
    print "Connected."
except Exception as e:
    print "I am unable to connect to the database::"
    print str(e)




def insertRaster(rastername, variable, source=source, resolution=resolution):
    tablename = uuid.uuid1().hex
    tablename = "data_" + str(tablename)
    print tablename
    r2pg = "raster2pgsql -s 4326 -d -I -C "
    r2pg += rastername
    r2pg += " -t 5x5 "
    r2pg += tablename

    sql = subprocess.Popen(r2pg, stdout=subprocess.PIPE, shell=True)
    (out, err) = sql.communicate()


    cursor = conn.cursor()

    cursor.execute(out)


    sql = "INSERT INTO rasterIndex VALUES(default, %s, %s, %s, default, %s);"
    cursor.execute(sql, (source, resolution, variable, tablename))

insertRaster("merged/prcp_1_merge.tiff", 12)
insertRaster("merged/prcp_2_merge.tiff", 17)
insertRaster("merged/prcp_3_merge.tiff", 18)
insertRaster("merged/prcp_4_merge.tiff", 19)
insertRaster("merged/prcp_5_merge.tiff", 20)
insertRaster("merged/prcp_6_merge.tiff", 21)
insertRaster("merged/prcp_8_merge.tiff", 22)
insertRaster("merged/prcp_9_merge.tiff", 23)
insertRaster("merged/prcp_10_merge.tiff", 24)
insertRaster("merged/prcp_11_merge.tiff", 25)
insertRaster("merged/prcp_12_merge.tiff", 26)

