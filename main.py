import os
import logging
from flask import Flask,render_template,request

from random import random, randint, shuffle, choice

from db import Database

import json

class Buckets:
    Unknown, Queue, Archive = range(3)

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
    return render_template('main.html')

@app.route("/study/vote/<study_id>/",methods=['POST'])
def post_new_vote(study_id):
    leftObj = Database.getPlace(request.form['left'])
    rightObj = Database.getPlace(request.form['right'])
    if leftObj is None or rightObj is None:
        return jsonifyResponse({
            'error': "Locations don't exist!"
        })
    leftObj['votes'] += 1
    rightObj['votes'] += 1
    leftObj['bucket'] = Buckets.Queue
    rightObj['bucket'] = Buckets.Queue
    Database.places.save(leftObj)
    Database.places.save(rightObj)
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
    unknownPlace = Database.places.find_one({
        'study_id' : study_id,
        'bucket' : Buckets.Unknown,
        'random' : {
            '$gte' : random()
        }
    })
    if unknownPlace is None:
        otherPlace = Database.places.find_one({
            'study_id' : study_id
        })
        if otherPlace is None:
            return jsonifyResponse({
                'error' : 'Could not find places for study!'
            })
        else:
            return jsonifyResponse({
                'error' : 'Study finished!',
                'study_finished' : True
            })
    knownPlace = Database.places.find_one({
        'study_id' : study_id,
        'bucket' : choice([Buckets.Queue, Buckets.Queue, Buckets.Archive]),
        'random' : {
            '$gte' : random()
        }
    })
    if knownPlace is None:
        # No known places yet. Grab another unknown.
        knownPlace = Database.places.find_one({
            'study_id' : study_id,
            'random' : {
                '$gte' : random()
        }
    })
    placesToDisplay = [knownPlace, unknownPlace]
    def reRandomize(place):
        place['random'] = random()
        Database.places.save(place)
    map(reRandomize,placesToDisplay)
    print placesToDisplay
    # Ensure that the known doesn't always appear on the left/unknown on the right
    shuffle(placesToDisplay)
    return jsonifyResponse({
        'locs' : map(objifyPlace, placesToDisplay)
    })

@app.route("/study/view/<study_id>/",methods=['GET'])
def server_view_study(study_id):
    return render_template('view_study.html',study_id=study_id)

@app.route("/study/create/")
def serve_create_study():
    return render_template('create_study.html')
    
@app.route('/study/create/',methods=['POST'])
def create_study():    
    # Insert the new study into Mongo
    newStudyID = Database.studies.insert({
        'question': request.form['question'],
        'maxVotes': request.form['maxVotes'],
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
        'random' : random(),
        'votes' : 0
    })
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