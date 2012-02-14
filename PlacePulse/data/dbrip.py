#!/usr/bin/python

import json

import MySQLdb

# Substitute user/pass info in connect() as necessary
conn = MySQLdb.connect(db='placepulse',user='root')
cur = conn.cursor()

# DB data
cities = dict()
locations = dict()

def rip_cities():
    conn.query("SELECT * FROM city")
    res = conn.store_result()
    
    def city_to_study(city_row):
        # city tuple is (id, city name, country)
        cities[city_row[0][0]] = city_row[0][1]
    
    for_result(city_to_study,res)

def rip_places():
    conn.query("SELECT * FROM places")
    res = conn.store_result()
    
    def save_place_json(place_row):
        place_row = place_row[0]
        # place tuple is (id,id_city,lat,lng,file_loc1,file_loc2,file_loc3,heading,pitch,mutant_of,id_location,total_votes)
        placeObj = {
            "loc" : [float(place_row[2]),float(place_row[3])],
            "heading" : place_row[7],
            "pitch" : place_row[8],
            "city" : cities.get(place_row[1]),
            "total_votes" : place_row[11],
            "sql_id" : place_row[0]
        }
        if place_row[9] is not None:
            placeObj['mutant_of'] = place_row[9]
        if not locations.get(place_row[10]):
            locations[place_row[10]] = []
        locations[place_row[10]].append(placeObj)

    for_result(save_place_json,res)
    
def write_locations():
    fo = open('mongo_dump.json','w')
    
    for (location_id,location_places) in locations.iteritems():
        locationObj = dict(location_id=location_id,places=location_places)
        fo.write(json.dumps(locationObj) + "\n")
    
    fo.close()
    
def for_result(func,results):
    res = results.fetch_row()
    while res != ():
        func(res)
        res = results.fetch_row()
    
rip_cities()
rip_places()
write_locations()