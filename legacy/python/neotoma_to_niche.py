__author__ = 'scottsfarley'

import requests
import psycopg2

print "Connecting..."
conn = psycopg2.connect(host="144.92.235.14", user="paleo", database="paleo", password="Alt0Sax!!")
cursor = conn.cursor()
cursor.execute("TRUNCATE TABLE NeotomaSampleData;")
conn.commit()
print "Connected."

taxa = requests.get("http://api.neotomadb.org/v1/data/taxa").json()

idx = 1
for taxon in taxa['data']:
    try:
        pct = (idx / len(taxa['data']))*100
        print taxon['TaxonName'], pct
        idx += 1
        taxonid = taxon['TaxonID']
        sampleDataURL = "http://api.neotomadb.org/v1/data/SampleData?taxonids=" + str(taxonid)
        sampleData = requests.get(sampleDataURL).json()
        print "\tFound", len(sampleData['data']), "occurrences."

        data = sampleData['data']
        for sd in data:
            lat = (float(sd['SiteLatitudeNorth']) + float(sd['SiteLatitudeSouth'])) / 2
            lng = (float(sd['SiteLongitudeWest']) + float(sd['SiteLongitudeEast'])) / 2
            age = sd['SampleAge']
            if age is None:
                try:
                    age = float(sd['SampleAgeYounger']) + float(sd['SampleAgeOlder']) / 2
                except:
                    continue
            datasetID = sd['DatasetID']
            grp = sd['TaxaGroup']
            sql = "INSERT INTO NeotomaSampleData VALUES(default, %(latitude)s, %(longitude)s, %(age)s,%(datasetid)s, %(taxonname)s, %(taxagroup)s);"
            cursor.execute(sql, {"latitude": lat, "longitude" : lng, "age" : age, "datasetid" : datasetID, "taxonname":taxon['TaxonName'], "taxagroup": grp})

        conn.commit()
    except Exception as e:
        print str(e)
        continue