#!/usr/bin/python

import json

import MySQLdb

from db import Database
# Substitute user/pass info in connect() as necessary
conn = MySQLdb.connect(db='PlacePulse',user='root')
cur = conn.cursor()

# DB data
cities = dict()
locations = dict()
studyidsD={}
locationsD={}
placeids = []
studyids=[]
study_mongo_ids=[]
locationids=[]
cityidset=set()
studyidset=set()
votes=[]
study_locs=[]


# Function ganked from python-iptools: http://code.google.com/p/python-iptools/
def long2ip (l):
    _MAX_IP = 0xffffffff
    _MIN_IP = 0x0
    if _MAX_IP < l or l < 0:
        raise TypeError("expected int between 0 and %d inclusive" % _MAX_IP)
    return '%d.%d.%d.%d' % (l>>24 & 255, l>>16 & 255, l>>8 & 255, l & 255) 

def SHA1(d):
    import hashlib
    h = hashlib.new('sha1')
    h.update(str(d))
    return h.hexdigest()

def for_result(func,results):
    res = results.fetch_row()
    while res != ():
        func(res)
        res = results.fetch_row()

def rip_cities():
    conn.query("SELECT * FROM city")
    res = conn.store_result()
    
    def city_to_place(city_row):
        # city tuple is (id, city name, country)
        #cities[city_row[0][0]] = "%s, %s" % (city_row[0][1],city_row[0][2])
        placeid = str(Database.places.insert({'name':city_row[0][1],
                'data_resolution':1000,
                'location_distribution':'randomly'}))
        cities[city_row[0][0]] = placeid
        placeids.append(placeid)
    for_result(city_to_place,res)


def rip_studies():
    conn.query("SELECT * FROM questions")
    res = conn.store_result()
    
    def save_study(study_row):
        # questions row is (id,question,id_study)
        studyid = str(Database.studies.insert({
                        'study_question': study_row[0][1],
                        'study_public': True,
                        'study_name':study_row[0][1],
                        'places_id':placeids}))
        studyids.append(study_row[0][0])
        study_mongo_ids.append(studyid)
        studyidsD[study_row[0][0]]=studyid
    
    for_result(save_study,res)


def rip_locations_and_places():
    # now, correlate places table with locations
    conn.query("SELECT * FROM places")
    res = conn.store_result()
    
    def save_place(place_row):
        # places row is (id, id_city, lat, lng, _, _, _, heading, pitch, mutant, id_location, total_votes)
        #print(place_row[1])
        if(place_row[1] not in cityidset):
            cityidset.add(place_row[1])
            placeid = str(Database.places.insert({'name':place_row[1],
                'data_resolution':1000,
                'location_distribution':'randomly'}))
            cities[place_row[1]] = placeid
            placeids.append(placeid)

        locationID=str(Database.locations.insert({'loc':[float(place_row[2]),float(place_row[3])],
                    'heading':place_row[7],
                    'pitch':place_row[8],
                    'type':'gsv',
                    'places_id':[cities[place_row[1]]]}))
    
        locationsD[int(place_row[0])]=str(locationID)
        locationids.append(locationID)
    for_result(save_place,res)
    
    
def rip_votes():
    conn.query("SELECT * FROM votes")
    
    res = conn.store_result()

    def save_vote(vote_row):
        from time import mktime           
        # vote_row is (id,id_question,id_left,id_left_city,id_right,id_right_city,winner,uuid_pulse,ip_address,timestamp)
        if(vote_row[1]!=0):
            studyID=studyidsD[vote_row[1]]
            leftID = locationsD[int(vote_row[2])]
            rightID = locationsD[int(vote_row[4])]
            if int(vote_row[6]) == leftID:
                choice = "left"
            elif int(vote_row[6]) == rightID:
                choice = "right"
            else:
                choice = "equal"
            Database.votes.insert({'study_id':studyID,
                    'left': leftID,
                    'right': rightID,
                    'left_city':cities[vote_row[3]] if vote_row[3] else None,
                    'right_city':cities[vote_row[5]] if vote_row[3] else None,
                    'choice':choice,
                    'timestamp': {
                        'date': int(mktime(vote_row[9].timetuple()))*1000
                    }})
            study_loc_dict[(studyID,leftID)]+=1
            study_loc_dict[(studyID,rightID)]+=1
    for_result(save_vote,res)

rip_cities()
#switched order of locations and studies because unknown cities are added in during the locations_and_places()
rip_locations_and_places()
rip_studies()
study_locs=[(studyID,locID) for studyID in study_mongo_ids for locID in locationids]
study_loc_dict={}
for x in study_locs:
    study_loc_dict[x]=0
rip_votes()
for x in study_loc_dict:
    Database.qs.insert({'study_id':x[0],
            'location_id':x[1],
            'num_votes':study_loc_dict[x]})
