from flask import Module
from flask import redirect,render_template,request

from util import *

study_builder = Module(__name__)

from db import Database

@study_builder.route("/study/create/")
def serve_create_study():
    cities=''
    for city in Database.studies.distinct('city'):
        if(len(str(city))>0):
            cities+=str(city)+','
    cities=cities[:-1]
    print('step one complete')
    return render_template('create_study.html', cities=cities)
    
@study_builder.route('/study/create/',methods=['POST'])
def create_study():    
    # Insert the new study into Mongo
    newStudyID = Database.studies.insert({
        'study_question': request.form['study_question'],
        'locations_requested': request.form['locations_requested'],
        'polygon': request.form['polygon'],
	'city': request.form['city']})
    print('finished')
    # Return the ID for the client to rendezvous at /study/populate/<id>
    return jsonifyResponse({
        'studyID': str(newStudyID)
    })

@study_builder.route('/study/populate/<study_id>/',methods=['GET'])
def serve_populate_study(study_id):
    study = Database.getStudy(study_id)
    return render_template('populate_study.html',polygon=study['polygon'],study_id=study_id)

@study_builder.route('/study/populate/<study_id>/',methods=['POST'])
def populate_study(study_id):
    Database.places.insert({
        'loc': [request.form['lat'],request.form['lng']],
        'study_id': request.form['study_id'],
        'bucket' : Buckets.Unknown,
        'votes' : 0
    })
    return jsonifyResponse({
        'success': True
    })

@study_builder.route('/study/finish_populate/<study_id>/',methods=['POST'])
def finish_populate_study(study_id):
    if Database.getStudy(study_id) is None:
        return jsonifyResponse({
            'error': 'Study doesn\'t exist!'
        })
    placesInQueue = Database.places.find({
        'study_id': study_id,
        'bucket': Buckets.Queue
    })
    placesToGet = Buckets.QueueSize-placesInQueue.count()

    # TODO: See if Mongo lets you do this in one update call.
    for i in range(placesToGet):
        place = Database.places.find_one({
            'study_id': study_id,
            'bucket': Buckets.Unknown
        })
        place['bucket'] = Buckets.Queue
        Database.places.save(place)
    
    return jsonifyResponse({
        'success': True
    })

@study_builder.route('/success/<study_id>',methods = ['GET'])
def success(study_id):
    cityname = Database.getStudy(study_id)['city']
    return render_template('successfullySaved.html',study_id=study_id, cityname = cityname)

@study_builder.route('/error/<error_id>')
def error(error_id):
    if(error_id=='1'):
        return render_template('errorpage.html',errorStatement = "Pick a better polygon.")
    return render_template('errorpage.html',errorStatement = "generic error statement")
