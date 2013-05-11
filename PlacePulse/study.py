from flask import Module

from flask import redirect,render_template,request,session,url_for

from gamify import Gamification
from util import *

from datetime import datetime
from random import random,randint
from uuid import uuid4


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
    #Insert new Place
    newPlaceID = Database.places.insert({
        'data_resolution': request.form['data_resolution'],
        'location_distribution': request.form['location_distribution'],
        'polygon': request.form['polygon'],
        'place_name': request.form['place_name'],
        'owner': session['userObj']['email'],
    })

    # Insert the new study into Mongo
    newStudyID = Database.studies.insert({
        'study_name': request.form['study_name'],
        'study_question': request.form['study_question'],
        'study_public': request.form['study_public'],
        'places_id': [newPlaceID],
        'owner': session['userObj']['email'],
        })
    session['currentStudy'] = newStudyID
    # Return the ID for the client to rendezvous at /study/populate/<id>
    return jsonifyResponse({
        'studyID': str(newStudyID),
        'placeID': str(newPlaceID)
    })

#--------------------Populate
@study.route('/place/populate/<place_id>/',methods=['GET'])
def serve_populate_place(place_id):
    place = Database.getPlace(place_id)
    return render_template('study_populate.html',polygon=place['polygon'],place_id=place_id,
                           locDist = place['location_distribution'], dataRes = place['data_resolution'], studyID=session['currentStudy'])

@study.route('/place/populate/<place_id>/<points_to_add>/',methods=['GET'])
def serve_populate_place_2(place_id, points_to_add):
    place = Database.getPlace(place_id)
    return render_template('study_populate_custompoints.html',polygon=place['polygon'],place_id=place_id,
                           locDist = place['location_distribution'], dataRes = place['data_resolution'], points_to_add = points_to_add, studyID=session['currentStudy'])

@study.route('/place/populate/<place_id>/',methods=['POST'])
def populate_place(place_id):
   location_id = Database.locations.insert({
       'loc': [request.form['lat'],request.form['lng']],
       'type':'gsv',
       'place_id': [place_id],
       'owner': session['userObj']['email'], #TODO: REAL LOGIN SECURITY
       'heading': 0,
       'pitch': 0,
       'votes':0
   })
   Database.qs.update({
       'location_id' : str(location_id),
       'study_id': str(session['currentStudy']),
       'place_id': place_id
   }, { '$set': {'num_votes' : 0 } }, True)
   return jsonifyResponse({
       'success': True
   })

@study.route('/place/finish_populate/<place_id>/',methods=['POST'])
def finish_populate_place(place_id):
    if Database.getPlace(place_id) is None:
        return jsonifyResponse({
            'error': 'Place doesn\'t exist!'
        })
    return jsonifyResponse({
        'success': True
    })

#--------------------Curate
@study.route('/place/curate/<place_id>/',methods=['GET'])
def curate_study(place_id):
    study_id = session['currentStudy']
    place = Database.getPlace(place_id)
    locations = Database.getLocations(place_id,48)
    return auto_template('study_curate.html',polygon=place['polygon'],locations=locations,place_id=place_id, study_id=study_id)

@study.route('/place/curate/<place_id>/<study_id>',methods=['GET'])
def curate_study_again(place_id,study_id):
    place = Database.getPlace(place_id)
    locations = Database.getLocations(place_id,48)
    return auto_template('study_curate.html',polygon=place['polygon'],locations=locations,place_id=place_id, study_id=study_id)

@study.route('/place/curate/location/<id>',methods=['POST'])
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

@study.route('/place/curate/location/update/<id>',methods=['POST'])
def update_location(id):
    lat = request.form['lat']
    lng = request.form['lng']
    heading = request.form['heading']
    pitch = request.form['pitch']
    locationUpdated = Database.updateLocation(id,heading,pitch)
    return jsonifyResponse({
    'success': str(locationUpdated)
    })

@study.route('/place/curate/location/delete/<id>',methods=['POST'])
def delete_location(id):
    locationDeleted = Database.deleteLocation(id)
    return jsonifyResponse({
    'success': str(locationDeleted)
    })

@study.route('/study/start/<study_id>/',methods=['GET'])
def start_start(study_id):
    #--Set study to "run"

    return auto_template('study_start.html',study_id=study_id)
#--------------------Vote
@study.route("/study/vote/<study_id>/",methods=['POST'])
def post_new_vote(study_id):
    def incVotes(obj):
        # Keep obj updates for consistency
        if obj.get('votes'):
            obj['votes'] += 1
        Database.locations.update({
            '_id': obj['_id']
        }, {
            '$inc': {
                'votes': 1
            }
        })
        Database.incQSVoteCount(study_id, str(obj.get('_id')))
    leftObj = Database.getLocation(request.form['left'])
    rightObj = Database.getLocation(request.form['right'])
    if leftObj is None or rightObj is None:
        return jsonifyResponse({
            'error': "Locations don't exist!"
        })
    map(incVotes, [leftObj,rightObj])
    newVoteObj = {
        'study_id' : request.form['study_id'],
        'left' : request.form['left'],
        'right' : request.form['right'],
        'choice' : request.form['choice'],
        'timestamp': datetime.now()
    }
    # If there is no userObj, create one now
    if not session.get('userObj'):
        # Generate a random ID to associate votes with this user if one does not already exist
        session['voterID'] = session['voterID'] if session.get('voterID') else str(uuid4().hex)
        session['userObj'] = Database.createUserObj(session['voterID'])
    if session['userObj'].get('email'):
        newVoteObj['voter_email'] = session['userObj']['email']
    if session.get('voterID'):
        newVoteObj['voter_uniqueid'] = session['voterID']
    # Insert vote into DB
    Database.votes.insert(newVoteObj)
    # Increment votes in DB
    Database.users.update({
        '_id': session['userObj']['_id']
    },
    {
        '$inc': {
            'num_votes': 1
        }
    })
    # And in cookied object
    session['userObj']['num_votes'] = session['userObj']['num_votes']+1 if session['userObj'].get('num_votes') else 1
    # Did the user unlock anything?
    unlockedStudies = Gamification.unlockNew(session['userObj'])
    if len(unlockedStudies) > 0:
        Database.users.update({
            '_id': session['userObj']['_id']
        }, {
            '$pushAll': {
                'unlocked_studies': unlockedStudies
            },
            '$set': {
                'last_unlocked_at': session['userObj']['num_votes']
            }
        })
        # Get user obj from database and update cookied object
        session['userObj'] = Database.getUserById(session['userObj']['_id'])
    session.modified = True
    response = {
        'success': True
    }
    # Finally, if the user requested an update to their gamification status, send it
    if request.form.get('gamification_status'):
        response['gamificationStatus'] = Gamification.getUnlockStatus(session['userObj'])
    return jsonifyResponse(response)

@study.route("/study/getpair/<study_id>/",methods=['GET'])
def get_study_pairing(study_id):
    # get location 1
    qs1 = Database.randomQS(study_id)
    if qs1 is None:
        return jsonifyResponse({
            'error': "Could not get location 1 from QS collection."
        })
    #get location 2
    loc_id = qs1['location_id']
    qs2 = Database.randomQS(study_id, exclude=loc_id)
    if qs2 is None:
        return jsonifyResponse({
            'error': "Could not get location 2 from QS collection."
        })

    # convert to location objects
    location1 = Database.getLocation(qs1['location_id'])
    location2 = Database.getLocation(qs2['location_id'])
    locationsToDisplay = [location1, location2]
    if location1 is None or location2 is None:
        return jsonifyResponse({
            'error': "Locations could not be retrieved from location collection!"
        })

    return jsonifyResponse({
        'locs' : map(objifyPlace, locationsToDisplay)
    })

#--------------------View
@study.route("/study/view/<study_id>/",methods=['GET'])
def server_view_study(study_id):
    studyObj = Database.getStudy(study_id)
    if studyObj is None:
        return redirect('/')
    votesCount = Database.getVotesCount(study_id)
    return auto_template('view_study.html',study_id=study_id,study_prompt=studyObj.get('study_question'),owner=studyObj.get('owner'),study_name=studyObj.get('study_name'), votes_contributed = votesCount)

@study.route('/location/view/<location_id>/',methods=['GET'])
def get_location(location_id):
    locationCursor = Database.getLocation(location_id)
    lat = locationCursor['loc'][0]
    lng = locationCursor['loc'][1]
    return "<img src='http://maps.googleapis.com/maps/api/streetview?size=404x296&location=" + lat + "," + lng + "&sensor=false'/>"
