from flask import Flask,redirect,request
app = Flask(__name__)
import os
import logging
import re
import pymongo
from db import Database
from util import *
from random import random
from trueskill import trueskill
import json
import time
import tornado.ioloop
import numpy as np


"""
Add a places field to each study.
On populating, use mongodb's update append to add it
To pull a random place, simply load the study obj, look at the places, and choose a random ID.

"""

# TODO: Move from modules to blueprints, see http://flask.pocoo.org/docs/blueprints/
from root import root
from admin import admin
from login import login
from matching import matching
from results import results
from study import study
app.register_module(root)
app.register_module(admin)
app.register_module(login)
app.register_module(matching)
app.register_module(results)
app.register_module(study)

app.secret_key = "a10ad1a40b754a4d9b663fac60556a78"

@app.route("/")
def main():
	studyObj = Database.getRandomStudy()
	if studyObj is None:
		return "Uh oh.. no study found in database."
	votesCount = Database.getVotesCount()
	return auto_template('main.html',study_id=studyObj.get('_id'),study_prompt=studyObj.get('study_question'), votes_contributed=votesCount, votes_for_study=studyObj['num_votes'])

def buildIndices():
    Database.qs.ensure_index([('study_id', pymongo.ASCENDING), ('location_id', pymongo.ASCENDING)]) # for updating the q scores after every vote
    Database.qs.ensure_index([ ('study_id', 1), ('random', 1) ]) # for quick selection of random pair of images for a given study
    Database.qs.ensure_index('trueskill.score') # for ranking purposes (e.g. showing top 10 and bottom 10 images from a given place/study)
    Database.db.qs_place.ensure_index([('study_id', pymongo.ASCENDING), ('place_id', pymongo.ASCENDING)]) # for updating the q scores of a place (city) after every vote
    # if there are not that many cities, this index is not necessary
    #Database.db.qs_place.ensure_index('trueskill.score') # for ranking purposes (e.g. showing top 10 and bottom 10 places for a given study)
    Database.locations.ensure_index("place_id") # for finding all the images for a given study by going through all the place_ids retrieved from a given study

    # Build spatial index
    #Database.places.ensureIndex({
    #    'loc': '2d'
    #})


def buildRandomPairs():
    print 'Rebuilding random pairs probability...'
    start = time.time()
    ### build study probabilities ###
    study_prob = []
    for study in Database.studs:
        nvotes = 0
        studyid = str(study['_id'])
        for qs_place in Database.qs_place.find({'study_id': studyid}): nvotes += qs_place['num_votes']
        print study['study_question'], nvotes
        study_prob.append(1.0/(nvotes+1))
    
    study_prob = np.array(study_prob)
    study_prob /= np.sum(study_prob)
    Database.study_prob = study_prob
    ### END build study probabilities ###
     
    ### build location probabilities ###
    locid2idx = Database.locid2idx
    locs = Database.locs
    studyid2prob = {}
    for study in Database.studies.find():
        studyid = str(study['_id'])
        prob = [0.0] * len(locs)
        for qs in Database.qs.find({'study_id': studyid}):
            idx = locid2idx[qs['location_id']]
            prob[idx] = 1.0/(qs['num_votes'] + 1)
        prob = np.array(prob)
        prob /= np.sum(prob)
        studyid2prob[studyid] = prob
    Database.studyid2prob = studyid2prob
    end = time.time()
    print 'Done rebuilding random pairs:', (end-start), 'sec'

def initDB():
  Database.studs = [study for study in Database.studies.find()]
  locid2idx = {}
  locs = [None] * Database.locations.count()
  i = 0
  for loc in Database.locations.find():
    locs[i] = loc
    locid2idx[str(loc['_id'])] = i
    i += 1
  
  Database.locid2idx = locid2idx
  Database.locs = locs
  print 'Done initializing db...'

buildIndices()
initDB()