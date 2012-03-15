from flask import Flask,redirect,render_template,request
app = Flask(__name__)

import os
import logging
import re

from db import Database
from util import *

import json

"""
Add a places field to each study.
On populating, use mongodb's update append to add it
To pull a random place, simply load the study obj, look at the places, and choose a random ID.

"""

# TODO: Move from modules to blueprints, see http://flask.pocoo.org/docs/blueprints/
from root import root
from admin import admin
from study import study
app.register_module(root)
app.register_module(admin)
app.register_module(study)



@app.route("/")
def main():
	studyObj = Database.getRandomStudy()
	if studyObj is None:
		return redirect('/')
	votesCount = Database.getVotesCount()
	return render_template('main.html',study_id=studyObj.get('_id'),study_prompt=studyObj.get('study_question'), votes_contributed=votesCount)

def buildIndices():
    # Build spatial index
    Database.places.ensureIndex({
        'loc': '2d'
    })
    
    Database.places.ensureIndex( { study_id : 1, random : 1, bucket : 1 } )
