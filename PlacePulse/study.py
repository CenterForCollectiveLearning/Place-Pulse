from flask import Module

from flask import redirect,render_template,request,url_for

from util import *

from datetime import datetime
from random import random

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
    return render_template('study_populate.html',polygon=study['polygon'],study_id=study_id,
                           locDist = study['location_distribution'], dataRes = study['data_resolution'])

@study.route('/study/populate/<study_id>/',methods=['POST'])
def populate_study(study_id):
    location_id = Database.locations.insert({
        'loc': [request.form['lat'],request.form['lng']],
        'study_id': request.form['study_id'],
        'heading': 0,
        'pitch': 0,
        'votes' : 0
    })
    Database.qs.update({
        'location_id' : location_id, 
        'study_id': request.form['study_id'],
    }, { '$set': {'num_votes' : 0 } }, True)    
    return jsonifyResponse({
        'success': True
    })

# TODO: Check if front end calls this function. Probably unnecessary
@study.route('/study/finish_populate/<study_id>/',methods=['POST'])
def finish_populate_study(study_id):
    if Database.getStudy(study_id) is None:
        return jsonifyResponse({
            'error': 'Study doesn\'t exist!'
        })
    return jsonifyResponse({
        'success': True
    })
    
#--------------------Curate
@study.route('/study/curate/<study_id>/',methods=['GET'])
def curate_study(study_id):
    study = Database.getStudy(study_id)
    locations = Database.getLocations(study_id,48)
    return auto_template('study_curate.html',polygon=study['polygon'],locations=locations,study_id=study_id)
    
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

@study.route('/study/start/<study_id>/',methods=['GET'])
def start_start(study_id):
    #--Set study to "run"
    
    return auto_template('study_start.html',study_id=study_id)
#--------------------Vote
@study.route("/study/vote/<study_id>/",methods=['POST'])
def post_new_vote(study_id):
    def incVotes(obj):
        obj['votes'] += 1
        Database.locations.save(obj)
        Database.incQSVoteCount(study_id, obj.get('_id'))

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
    print "saving choice: %s" % request.form['choice']
    return jsonifyResponse({
        'success': True
    })

@study.route("/study/getpair/<study_id>/",methods=['GET'])
def get_study_pairing(study_id):
    # get location 1
    QS1 = Database.randomQS(study_id, fewestVotes=True)
    
    #get location 2
    try:
        if QS1.get('q', None) is None: # location 1 has no q score
            QS2 = Database.randomQS(study_id, exclude=QS1.get('location_id')) 
        else:
            #get 25 locations with q scores
            obj = { 
                'study_id': study_id,
                'location_id' : { '$ne' : location1.get('_id') },
                'num_votes' : { '$lte' : 30 },
                'q' : { '$exists' : True }
            }
            count = Database.qs.find(obj).count()
            rand = randint(0,min(0,count-25))
            QSCursor = Database.qs.find(obj).skip(rand).limit(25)            
            
            #pick location with closest score
            dist = lambda QS: abs(QS.get('q') - QS1['q'])
            QS2 = min(QSCursor, key=dist)
    except:
         return jsonifyResponse({ 'error': "Cannot get location 2." })

    # convert to location objects
    toLocation = lambda QS: Database.getLocation(QS.get('location_id'))
    locationsToDisplay = map(toLocation, [QS1, QS2])
    print "left: %s" % QS1.get("location_id")
    print "right: %s" % QS2.get("location_id")

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
@study.route('/results/<studyName>/',methods = ['GET'])
def showSpecificBigStudyResults(studyName):
    return showBigStudyResults(studyName)

@study.route('/results/',methods = ['GET'])
def showBigStudyResults(studyName='unique'):
    # 'unique' is the default study
    studyQuestions = [
        ("Which place looks more unique?","unique"),
        ("Which place looks safer?","safer"),
        ("Which place looks more upper class?","upper_class"),
        ("Which place looks more lively?","lively"),
        ("Which place looks more modern?","modern"),
        ("Which place looks more central?","central"),
        ("Which place looks more groomed?","groomed")
    ]
    return auto_template('results.html', study_name=studyName, study_questions=studyQuestions)
    
@study.route('/results_data/<studyName>/',methods = ['GET'])
def getResultsData(studyName):
    return jsonifyResponse(Database.getResultsForStudy(studyName))

@study.route('/city_results_data/<studyName>/<cityName>/',methods = ['GET'])
def getCityResultsData(studyName,cityName):
    studyResults = Database.getResultsForStudy(studyName)
    cityResults = [i for i in studyResults['ranking'] if i['city_name_id'] == cityName]
    retObj = {
            'question': studyResults['question'],
            'question_shortid': studyResults['question_shortid'],
            'ranking': cityResults
    }
    return jsonifyResponse(retObj)

@study.route('/top_results_data/<studyName>/',methods = ['GET'])
def getTopResultsData(studyName):
    studyResults = Database.getResultsForStudy(studyName)
    # To save space, show only the top and bottom 3 for each city
    for city in studyResults['ranking']:
        city['top'] = city['places'][0:3]
        city['bottom'] = city['places'][-3:]
        del city['places']
    return jsonifyResponse(studyResults)
    
@study.route('/rankings/<studyName>/<cityNameId>/',methods = ['GET'])
def getCityResults(cityNameId,studyName):
    return auto_template('city_results.html',city_name_id=cityNameId, study_name=studyName)
    
# @study.route('/rankings_data/<cityNameId>/',methods = ['GET'])    
# def getCityResultsData(cityNameId):
#     mainStudyResults = [i for i in Database.results.find({'study_type': 'main_study'})]
#     cityResults = []
#     for results in mainStudyResults:
#         resultsForStudy = [i for i in results['ranking'] if i['city_name_id'] == cityNameId]
#         cityResults.append({
#             'question': results['question'],
#             'question_shortid': results['question_shortid'],
#             'ranking': resultsForStudy
#         })
#     return jsonifyResponse(cityResults)

# @study.route('/results/<study_id>/',methods = ['GET'])
# def showData(study_id):
#     L=""
#     for x in Database.votes.find({'study_id':study_id}):
#         leftStuff = re.sub("[^,0123456789.-]",'',str(Database.getPlace(x['left'])['loc']))
#         rightStuff = re.sub("[^,0123456789.-]",'',str(Database.getPlace(x['right'])['loc']))
#         L+=str(leftStuff)+","+str(rightStuff)+","+str(x['choice'])+","
#     L=L[:-1]
#     return auto_template('results.html',study_id=study_id, L=L)
