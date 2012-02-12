from flask import Module
from flask import redirect,render_template,request

from util import *

study = Module(__name__)

from db import Database

#--------------------Create
@study.route("/study/create/")
def serve_create_study():
    cities=''
    for city in Database.studies.distinct('city'):
        if(len(str(city))>0):
            cities+=str(city)+','
    cities=cities[:-1]
    return render_template('study_create.html', cities=cities)
    
@study.route('/study/create/',methods=['POST'])
def create_study():    
    # Insert the new study into Mongo
    newStudyID = Database.studies.insert({
        'study_name': request.form['study_question'],
        'study_question': request.form['study_question'],
		'study_public': request.form['study_public'],
        'data_resolution': request.form['data_resolution'],
        'location_distribution': request.form['location_distribution'],
		'polygon': request.form['polygon']})
    # Return the ID for the client to rendezvous at /study/populate/<id>
    return jsonifyResponse({
        'studyID': str(newStudyID)
    })

#--------------------Populate
@study.route('/study/populate/<study_id>/',methods=['GET'])
def serve_populate_study(study_id):
    study = Database.getStudy(study_id)
    return render_template('study_populate.html',polygon=study['polygon'],study_id=study_id)

@study.route('/study/populate/<study_id>/',methods=['POST'])
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

@study.route('/study/finish_populate/<study_id>/',methods=['POST'])
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

@study.route('/success/<study_id>',methods = ['GET'])
def success(study_id):
    cityname = Database.getStudy(study_id)['city']
    return render_template('successfullySaved.html',study_id=study_id, cityname = cityname)

@study.route('/error/<error_id>')
def error(error_id):
    if(error_id=='1'):
        return render_template('errorpage.html',errorStatement = "Pick a better polygon.")
    return render_template('errorpage.html',errorStatement = "generic error statement")

#--------------------Vote
@study.route("/study/vote/<study_id>/",methods=['POST'])
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

@study.route("/study/getpair/<study_id>/",methods=['GET'])
def get_study_pairing(study_id):
    placesInQueueCursor = Database.places.find({ 'bucket': Buckets.Queue, 
                            'study_id': study_id }).limit(Buckets.QueueSize)
    placesInQueue = [place for place in placesInQueueCursor]

    placesToDisplay = sample(placesInQueue,2)
    return jsonifyResponse({
        'locs' : map(objifyPlace, placesToDisplay)
    })

#--------------------View
@study.route("/study/view/<study_id>/",methods=['GET'])
def server_view_study(study_id):
    studyObj = Database.getStudy(study_id)
    if studyObj is None:
        return redirect('/')
    return render_template('view_study.html',study_id=study_id,study_prompt=studyObj.get('study_question'))

@study.route('/place/view/<place_id>/',methods=['GET'])
def get_place(place_id):
	placeCursor = Database.getPlace(place_id)
	lat = placeCursor['loc'][0]
	lng = placeCursor['loc'][1]
	return "<img src='http://maps.googleapis.com/maps/api/streetview?size=404x296&location=" + lat + "," + lng + "&sensor=false'/>"

#--------------------Results
@study.route('/results/<study_id>/',methods = ['GET'])
def showData(study_id):
    L=""
    for x in Database.votes.find({'study_id':study_id}):
        leftStuff = re.sub("[^,0123456789.-]",'',str(Database.getPlace(x['left'])['loc']))
        rightStuff = re.sub("[^,0123456789.-]",'',str(Database.getPlace(x['right'])['loc']))
        L+=str(leftStuff)+","+str(rightStuff)+","+str(x['choice'])+","
    L=L[:-1]
    return render_template('results.html',study_id=study_id, L=L)
