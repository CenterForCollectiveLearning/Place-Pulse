from flask import Module
from flask import redirect,render_template,request

import re
from random import sample
from util import *

study_viewer = Module(__name__)

from db import Database

@study_viewer.route("/study/vote/<study_id>/",methods=['POST'])
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

@study_viewer.route("/study/getpair/<study_id>/",methods=['GET'])
def get_study_pairing(study_id):
    placesInQueueCursor = Database.places.find({ 'bucket': Buckets.Queue, 
                            'study_id': study_id }).limit(Buckets.QueueSize)
    placesInQueue = [place for place in placesInQueueCursor]
    
    placesToDisplay = sample(placesInQueue,2)
    return jsonifyResponse({
        'locs' : map(objifyPlace, placesToDisplay)
    })

@study_viewer.route("/study/view/<study_id>/",methods=['GET'])
def server_view_study(study_id):
    studyObj = Database.getStudy(study_id)
    if studyObj is None:
        return redirect('/')
    return render_template('view_study.html',study_id=study_id,study_prompt=studyObj.get('study_question'))

@study_viewer.route('/place/view/<place_id>/',methods=['GET'])
def get_place(place_id):
	placeCursor = Database.getPlace(place_id)
	lat = placeCursor['loc'][0]
	lng = placeCursor['loc'][1]
	return "<img src='http://maps.googleapis.com/maps/api/streetview?size=404x296&location=" + lat + "," + lng + "&sensor=false'/>"

@study_viewer.route('/results/<study_id>/',methods = ['GET'])
def showData(study_id):
    L=""
    for x in Database.votes.find({'study_id':study_id}):
        leftStuff = re.sub("[^,0123456789.-]",'',str(Database.getPlace(x['left'])['loc']))
        rightStuff = re.sub("[^,0123456789.-]",'',str(Database.getPlace(x['right'])['loc']))
        L+=str(leftStuff)+","+str(rightStuff)+","+str(x['choice'])+","
    L=L[:-1]
    return render_template('results.html',study_id=study_id, L=L)