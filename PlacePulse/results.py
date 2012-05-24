from flask import Module

from flask import redirect,render_template,request,url_for

from util import *

from datetime import datetime
from random import random
from random import randint

results = Module(__name__)

from db import Database

#--------------------Results
@results.route('/results/',methods = ['GET'])
def showBigStudyResults():
    featuredStudies = [i for i in Database.studies.find({
        'featured': True
    })]
    if len(featuredStudies) == 0:
        # No featured studies, just grab 5 regular ones and hope for the best.
       featuredStudies = [i for i in Database.studies.find({}).limit(50)] 
    return auto_template('results_landing.html',studies=[strFromObjectID(i) for i in featuredStudies])

@results.route('/study/results/<study_id>/',methods = ['GET'])
def showUserStudyResults(study_id):
    studyObj = Database.getStudy(study_id)
    return auto_template('study_results.html',study=studyObj)

@results.route('/study/results_data/<study_id>/',methods = ['GET'])
def getUserStudyResultsData(study_id):
    results = Database.getResultsForStudy(study_id).get('results')
    return jsonifyResponse(results)
    
@results.route('/study/top_results_data/<study_id>/',methods = ['GET'])
def getUserStudyResultsData(study_id):
    # Just get the top and bottom 8 for each city
    results = Database.getResultsForStudy(study_id).get('results')
    for place in results['ranking']:
        place['top'] = place['rankings'][0:8]
        place['bottom'] = place['rankings'][-8:]
        del place['rankings']
    return jsonifyResponse(results)

@results.route('/study/results/<study_id>/<place_name_slug>/',methods = ['GET'])
def showPlaceResultsForStudy(study_id,place_name_slug):
    studyObj = Database.getStudy(study_id)
    results = Database.getResultsForStudy(study_id).get('results')
    return auto_template('place_results.html',study=studyObj,results=results)

@results.route('/study/results_data/<study_id>/<place_name_slug>/',methods = ['GET'])
def getPlaceResultsForStudyData(study_id,place_name_slug):
    results = Database.getResultsForStudy(study_id).get('results')
    results['ranking'] = [i for i in results['ranking'] if i['name_slug'] == place_name_slug]
    return jsonifyResponse(results)
