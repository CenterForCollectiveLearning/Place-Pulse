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
from study_admin import study_admin
from study_builder import study_builder
from study_viewer import study_viewer
app.register_module(study_admin)
app.register_module(study_builder)
app.register_module(study_viewer)


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