from db import Database

from flask import Module

from flask import redirect,render_template,request,session,url_for

from util import *

matching = Module(__name__)

def getNewPrompt():
    # FIXME:
    # Mongo won't allow us to query for studies with greater than N places, so we'll just do a scan of all the studies here
    # and hope there aren't too many in the database!
    from random import choice, sample
    study = choice([i for i in Database.studies.find() if i.get('places_id') and len(i['places_id']) >= 4])
    placeIDs = [placeID for placeID in study['places_id'] if Database.locations.find({"places_id": placeID}).count() > 0]   
    # From the randomly chosen study, choose four places randomly
    places = [Database.getPlace(placeID) for placeID in sample(placeIDs,4)]
    locs = [Database.getRandomLocationByPlace(place['_id']) for place in places]
    # print "1: " + str([p['_id'] for p in places])
    # print "2: " + str(placeIDs)
    # return jsonifyResponse(places)
    return {
        "locs": [dict([('id',loc['_id']),('coords',loc['loc'])]) for loc in locs],
        "place_names": places
    }    

def getDefaultPrompt():
    return {
        "locs": [
            {
                "id": "1",
                "coords": [40.7321,-73.9924]
            },
            {
                "id": "2",
                "coords": [48.8591,2.3153]
            },
            {
                "id": "3",
                "coords": [51.517,-0.127]
            },
            {
                "id": "4",
                "coords": [34.090,-118.359]
            }
        ],
        "place_names": [
            {
                "name": "Paris, France"
            },
            {
                "name": "New York City, USA"
            },
            {
                "name": "London, UK"
            },
            {
                "name": "Los Angeles, USA"
            },
        ]
    }

#--------------------Main
@matching.route("/matching/")
def serve_matching_page():
    return auto_template('matching.html')
    
@matching.route("/matching/get_prompt/")
def get_matching_prompt():
    return jsonifyResponse(getNewPrompt())

@matching.route("/matching/eval_solution/",methods=['POST'])
def eval_matching_solution():
    from random import randint
    return jsonifyResponse({
        "num_correct": randint(0,4),
        "next_prompt": getNewPrompt()
    })