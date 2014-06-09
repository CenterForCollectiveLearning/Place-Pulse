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
    Database.qs.ensure_index('trueskill.score') # for ranking purposes (e.g. showing top 10 and bottom 10 images from a given place/study)
    Database.db.qs_place.ensure_index([('study_id', pymongo.ASCENDING), ('place_id', pymongo.ASCENDING)]) # for updating the q scores of a place (city) after every vote
    # if there are not that many cities, this index is not necessary
    #Database.db.qs_place.ensure_index('trueskill.score') # for ranking purposes (e.g. showing top 10 and bottom 10 places for a given study)
    Database.locations.ensure_index("place_id") # for finding all the images for a given study by going through all the place_ids retrieved from a given study

def initDB():
  Database.studs = list(Database.studies.find())
  Database.biased_studs = [study for study in Database.studs if study['study_question'] in  ['safer','livelier']]
  Database.study2activeLocID = {}
  Database.locs = {}
  for loc in list(Database.locations.find()):
    Database.locs[str(loc['_id'])] = loc
  print 'Total # of locations', len(Database.locs)
  for study in Database.studs:
    study_id = str(study['_id'])
    Database.study2activeLocID[study_id] = {}
    activeLocID = Database.study2activeLocID[study_id]
    for qs in list(Database.qs.find({'study_id': study_id})):
        if 'active' in qs and qs['active'] == 0: continue
        activeLocID[qs['location_id']] = True
    print study_id, '# of active locations', len(activeLocID)
  print 'Done initializing db...'

buildIndices()
initDB()