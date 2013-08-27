import os
import json
import csv

from db import Database

with open('pulse_locations_dump.csv', 'wb') as csvfile:
  csvwriter = csv.writer(csvfile, delimiter=",")
  for location in Database.locations.find():
    lat = location["loc"][0]
    lng = location["loc"][1]
    pitch = location["pitch"]
    heading = location["heading"]
    csvwriter.writerow([lat, lng, pitch, heading])

