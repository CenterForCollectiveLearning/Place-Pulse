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

app.secret_key = os.environ['COOKIE_SECRET_KEY']

@app.route("/")
def main():
	studyObj = Database.getRandomStudy()
	if studyObj is None:
		return "I don't have any studies. Go to /study/create and make one."
	votesCount = Database.getVotesCount()
	return auto_template('main.html',study_id=studyObj.get('_id'),study_prompt=studyObj.get('study_question'), votes_contributed=votesCount)

def buildIndices():
    Database.qs.ensure_index([('study_id', pymongo.ASCENDING), ('location_id', pymongo.ASCENDING)]) # for updating the q scores after every vote
    Database.qs.ensure_index([ ('study_id', pymongo.ASCENDING), ('random', pymongo.ASCENDING) ]) # for quick selection of random pair of images for a given study
    Database.qs.ensure_index('trueskill.score') # for ranking purposes (e.g. showing top 10 and bottom 10 images from a given place/study)
    Database.db.qs_place.ensure_index([('study_id', pymongo.ASCENDING), ('place_id', pymongo.ASCENDING)]) # for updating the q scores of a place (city) after every vote
    # if there are not that many cities, this index is not necessary
    #Database.db.qs_place.ensure_index('trueskill.score') # for ranking purposes (e.g. showing top 10 and bottom 10 places for a given study)
    Database.locations.ensure_index("place_id") # for finding all the images for a given study by going through all the place_ids retrieved from a given study

    # Build spatial index
    #Database.places.ensureIndex({
    #    'loc': '2d'
    #})


buildIndices()