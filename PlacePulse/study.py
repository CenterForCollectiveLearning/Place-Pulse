from flask import Module

from flask import redirect,render_template,request,url_for

from util import *

from datetime import datetime
from random import sample

study = Module(__name__)

from db import Database

#--------------------Create
@study.route("/study/create/")
def serve_create_study():
    if getLoggedInUser() is None:
        return redirect(url_for('login.signin',next="/study/create"))
    return auto_template('study_create.html')
    
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
    return auto_template('study_populate.html',polygon=study['polygon'],study_id=study_id)

@study.route('/study/populate/<study_id>/',methods=['POST'])
def populate_study(study_id):
    Database.locations.insert({
        'loc': [request.form['lat'],request.form['lng']],
        'study_id': request.form['study_id'],
        'heading': 0,
        'pitch': 0,
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
    locationsInQueue = Database.locations.find({
        'study_id': study_id,
        'bucket': Buckets.Queue
    })
    locationsToGet = Buckets.QueueSize-locationsInQueue.count()

    # TODO: See if Mongo lets you do this in one update call.
    for i in range(locationsToGet):
        location = Database.locations.find_one({
            'study_id': study_id,
            'bucket': Buckets.Unknown
        })
        location['bucket'] = Buckets.Queue
        Database.locations.save(location)
    
    return jsonifyResponse({
        'success': True
    })
    
#--------------------Curate
@study.route('/study/curate/<study_id>/',methods=['GET'])
def curate_study(study_id):
    study = Database.getStudy(study_id)
    locations = Database.getLocations(study_id)
    return auto_template('study_curate.html',polygon=study['polygon'],locations=locations)
    
@study.route('/study/curate/location/<id>',methods=['POST'])
def curate_location():    
    # Insert the new study into Mongo
    location = Database.getLocation(id)
    # Return the ID for the client to rendezvous at /study/populate/<id>
    return jsonifyResponse({
        'latitude': str(location.loc[0]),
        'longitude': str(location.loc[1]),
        'heading': str(location.heading),
        'pitch': str(location.pitch)
    })

@study.route('/study/curate/location/update/<id>',methods=['POST'])
def update_location(id):
    lat = request.form['lat']
    lng = request.form['lng']
    heading = request.form['heading']
    pitch = request.form['pitch']
    locationUpdated = Database.updateLocation(id,heading,pitch)
    return jsonifyResponse({
    'success': str(locationUpdated)
    })
    
@study.route('/study/curate/location/delete/<id>',methods=['POST'])
def delete_location(id):
    locationDeleted = Database.deleteLocation(id)
    return jsonifyResponse({
    'success': str(locationDeleted)
    })

#--------------------Vote
@study.route("/study/vote/<study_id>/",methods=['POST'])
def post_new_vote(study_id):
    def incVotes(obj):
        obj['votes'] += 1
        if obj['votes'] > 30:
            obj.bucket = Buckets.Archive

            newForQueue = Database.locations.find_one({ 'bucket': Buckets.Unknown })
            newForQueue['bucket'] = Buckets.Queue
            Database.locations.save(newForQueue)
        Database.locations.save(obj)


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
        'choice' : request.form['choice'],
        'timestamp': datetime.now()
    })
    return jsonifyResponse({
        'success': True
    })

@study.route("/study/getpair/<study_id>/",methods=['GET'])
def get_study_pairing(study_id):
    locationsInQueueCursor = Database.locations.find({ 'bucket': Buckets.Queue, 
                            'study_id': study_id }).limit(Buckets.QueueSize)
    locationsInQueue = [location for location in locationsInQueueCursor]
    locationsToDisplay = sample(locationsInQueue,2)
    return jsonifyResponse({
        'locs' : map(objifyPlace, locationsToDisplay)
    })

#--------------------View
@study.route("/study/view/<study_id>/",methods=['GET'])
def server_view_study(study_id):
    studyObj = Database.getStudy(study_id)
    if studyObj is None:
        return redirect('/')
    return auto_template('view_study.html',study_id=study_id,study_prompt=studyObj.get('study_question'))

@study.route('/location/view/<location_id>/',methods=['GET'])
def get_location(location_id):
	locationCursor = Database.getPlace(location_id)
	lat = locationCursor['loc'][0]
	lng = locationCursor['loc'][1]
	return "<img src='http://maps.googleapis.com/maps/api/streetview?size=404x296&location=" + lat + "," + lng + "&sensor=false'/>"

#--------------------Results
@study.route('/results/',methods = ['GET'])
def showBigStudyResults():
    return auto_template('results.html')
    
@study.route('/results_data/',methods = ['GET'])
def getResultsData():
    safestCityResults = {
        'question': "Which place looks more unique?",
        'ranking': [
            {
                'city_name': 'Sao Paulo',
                'top': [{'coords': [-23.547865000000002, -46.675600000000031], 'type': 'streetview'}, {'coords': [-23.541809000000001, -46.642515000000003], 'type': 'streetview'}, {'coords': [-23.530771000000001, -46.651857000000007]}],
                'bottom': [{'coords': [-23.600961999999999, -46.654426999999998], 'type': 'streetview'}, {'coords': [-23.566029, -46.613223000000005], 'type': 'streetview'}, {'coords': [-23.588011000000002, -46.668845000000033], 'type': 'streetview'}]
            },
            {
                'city_name': 'New York City',
                'top': [{'coords': [40.766919999999999, -73.898903000000018], 'type': 'streetview'}, {'coords': [40.799993999999998, -73.913370999999984], 'type': 'streetview'}, {'coords': [40.737164999999997, -73.885324999999966], 'type': 'streetview'}],
                'bottom': [{'coords': [40.74297, -73.891733999999985], 'type': 'streetview'}, {'coords': [40.711815000000001, -73.807912999999985], 'type': 'streetview'}, {'coords': [40.687119000000003, -73.949285000000032], 'type': 'streetview'}]
            },
            {
                'city_name': 'Los Angeles',
                'top': [{'coords': [33.997357999999998, -118.28591], 'type': 'streetview'}, {'coords': [33.991506000000001, -118.39314000000002], 'type': 'streetview'}, {'coords': [34.019933999999999, -118.37815399999999], 'type': 'streetview'}],
                'bottom': [{'coords': [33.939588999999998, -118.348253], 'type': 'streetview'}, {'coords': [33.983154999999996, -118.33376900000002], 'type': 'streetview'}, {'coords': [34.017209999999999, -118.27480800000001], 'type': 'streetview'}]
            },
            {
                'city_name': 'Tokyo',
                'top': [{'coords': [35.680777999999997, 139.71636599999999], 'type': 'streetview'}, {'coords': [35.63702, 139.74308799999994], 'type': 'streetview'}, {'coords': [35.676063999999997, 139.65205000000003], 'type': 'streetview'}],
                'bottom': [{'coords': [35.703251999999999, 139.75068299999998], 'type': 'streetview'}, {'coords': [35.706812999999997, 139.77918699999998], 'type': 'streetview'}, {'coords': [35.727221999999998, 139.86986000000002], 'type': 'streetview'}]
            },
            {
                'city_name': 'Mexico City',
                'top': [{'coords': [19.424503999999999, -99.13759600000003], 'type': 'streetview'}, {'coords': [19.457988, -99.116128000000003], 'type': 'streetview'}, {'coords': [19.445329000000001, -99.147404999999992], 'type': 'streetview'}],
                'bottom': [{'coords': [19.458265999999998, -99.133131999999989], 'type': 'streetview'}, {'coords': [19.414881000000001, -99.139445000000023], 'type': 'streetview'}, {'coords': [19.401679000000001, -99.021538000000021], 'type': 'streetview'}]
            }
        ]
    }
    return jsonifyResponse(safestCityResults)


@study.route('/results/<study_id>/',methods = ['GET'])
def showData(study_id):
    L=""
    for x in Database.votes.find({'study_id':study_id}):
        leftStuff = re.sub("[^,0123456789.-]",'',str(Database.getPlace(x['left'])['loc']))
        rightStuff = re.sub("[^,0123456789.-]",'',str(Database.getPlace(x['right'])['loc']))
        L+=str(leftStuff)+","+str(rightStuff)+","+str(x['choice'])+","
    L=L[:-1]
    return auto_template('results.html',study_id=study_id, L=L)
