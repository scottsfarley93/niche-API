__author__ = 'scottsfarley'


import psycopg2

conn = psycopg2.connect(database="paleo", host="144.92.235.14", user="paleo", password="Alt0Sax!!")

if conn is None or not conn:
    print "Failed"
else:
    print "Success."

inTableQuery = "SELECT * FROM rasterIndex;"

allTableQuery = "SELECT table_name FROM information_schema.tables WHERE table_schema='public' "

cursor = conn.cursor()

cursor.execute(allTableQuery)


allTables = []
for record in cursor:
    allTables.append(record[0])

cursor.execute(inTableQuery)


inTables = []
for record in cursor:
    inTables.append(record[-1])

for tableName in allTables:
    if tableName[0:4] == "data":
        if tableName not in inTables:
            sql = "DROP TABLE " + str(tableName) + ";"
            cursor.execute(sql)
            conn.commit()
