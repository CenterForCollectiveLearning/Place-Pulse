import os
import logging
from flask import Flask,redirect,render_template,request

from random import random, randint, shuffle, choice, sample

from db import Database

import json


"""
Add a places field to each study.
On populating, use mongodb's update append to add it
To pull a random place, simply load the study obj, look at the places, and choose a random ID.

"""

class Buckets:
    Unknown, Queue, Archive = range(3)
    QueueSize = 100

app = Flask(__name__)

def jsonifyResponse(obj):
    resp = app.make_response(json.dumps(obj))
    resp.mimetype = 'application/json'
    return resp

def objifyPlace(place):
    return {
        'id' : str(place['_id']),
        'loc' : place['loc']
    }

@app.route("/")
def main():
	studyObj = Database.getRandomStudy()
	if studyObj is None:
		return redirect('/')
	votesCount = Database.getVotes()
	return render_template('main.html',study_id=studyObj.get('_id'),study_prompt=studyObj.get('study_question'), votes_contributed=votesCount)

@app.route("/study/vote/<study_id>/",methods=['POST'])
def post_new_vote(study_id):
    def incVotes(obj):
        obj['votes'] += 1
        if obj['votes'] > 30:
            obj.bucket = Buckets.Archive
            
            newForQueue = Database.places.find_one({ 'bucket': Buckets.Unknown })
            newForQueue['bucket'] = Buckets.Queue
            Database.places.save(newForQueue)
        Database.places.save(obj)
        
    
    leftObj = Database.getPlace(request.form['left'])
    rightObj = Database.getPlace(request.form['right'])
    if leftObj is None or rightObj is None:
        return jsonifyResponse({
            'error': "Locations don't exist!"
        })
    map(incVotes, [leftObj,rightObj])
    Database.votes.insert({
        'study_id' : request.form['study_id'],
        'left' : request.form['left'],
        'right' : request.form['right'],
        'choice' : request.form['choice']
    })
    return jsonifyResponse({
        'success': True
    })

@app.route("/study/getpair/<study_id>/",methods=['GET'])
def get_study_pairing(study_id):
    placesInQueueCursor = Database.places.find({ 'bucket': Buckets.Queue, 
                            'study_id': study_id }).limit(Buckets.QueueSize)
    placesInQueue = [place for place in placesInQueueCursor]
    
    placesToDisplay = sample(placesInQueue,2)
    return jsonifyResponse({
        'locs' : map(objifyPlace, placesToDisplay)
    })

@app.route("/admin/rank/<study_id>/",methods=['GET'])
def calculate_ranking(study_id):
	votes = Database.getVotes(study_id)
	for vote in votes:
		print vote

"""
@app.route("/admin/rank/")
def get_study_pairing():
    placesInQueueCursor = Database.places.find({ 'bucket': Buckets.Queue, 
                            'study_id': study_id }).limit(Buckets.QueueSize)
    placesInQueue = [place for place in placesInQueueCursor]

    placesToDisplay = sample(placesInQueue,2)
    return jsonifyResponse({
        'locs' : map(objifyPlace, placesToDisplay)
    })
"""

@app.route("/study/view/<study_id>/",methods=['GET'])
def server_view_study(study_id):
    studyObj = Database.getStudy(study_id)
    if studyObj is None:
        return redirect('/')
    return render_template('view_study.html',study_id=study_id,study_prompt=studyObj.get('study_question'))

@app.route("/study/create/")
def serve_create_study():
    return render_template('create_study.html')
    
@app.route('/study/create/',methods=['POST'])
def create_study():    
    # Insert the new study into Mongo
    newStudyID = Database.studies.insert({
        'study_question': request.form['study_question'],
        'locations_requested': request.form['locations_requested'],
        'polygon': request.form['polygon']})
    # Return the ID for the client to rendezvous at /study/populate/<id>
    return jsonifyResponse({
        'studyID': str(newStudyID)
    })

@app.route('/study/populate/<study_id>/',methods=['GET'])
def serve_populate_study(study_id):
    study = Database.getStudy(study_id)
    return render_template('populate_study.html',polygon=study['polygon'],study_id=study_id)

@app.route('/study/populate/<study_id>/',methods=['POST'])
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

@app.route("/admin/")
def load_admin():
	return render_template('admin.html')

@app.route('/study/finish_populate/<study_id>/',methods=['POST'])
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

def buildIndices():
    # Build spatial index
    Database.places.ensureIndex({
        'loc': '2d'
    })
    
    Database.places.ensureIndex( { study_id : 1, random : 1, bucket : 1 } )

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.logger.setLevel(logging.DEBUG)
    app.config.update(DEBUG=True,PROPAGATE_EXCEPTIONS=True,TESTING=True)
    app.run(debug=True,host='0.0.0.0',port=port)