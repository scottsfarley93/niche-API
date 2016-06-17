import requests
import json

url = "http://localhost:8080/data"

data = {
    'locations' : [{
        'latitude' : 37,
        'longitude' : -122,
        'yearsBP' : 0
    },
        {
        'latitude' : 36,
        'longitude' : -100,
        'yearsBP' : 1000
        }
    ]

}
headers = {
    'content-type': 'application/json'
}

r = requests.post(url, data=json.dumps(data), headers=headers)

print r
print r.text
