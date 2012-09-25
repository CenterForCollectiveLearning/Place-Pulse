from flask import Module
from flask import redirect,request

from random import sample
from util import *

admin = Module(__name__)

from db import Database

@admin.route("/admin/")
def load_admin():
    if getLoggedInUser() is None:
        return redirect("/login/")
    studies = Database.getStudies(session['userObj']['email'])
    return auto_template('admin.html',studies=studies)

@admin.route("/admin/all_studies")
def load_admin_studies():
    if getLoggedInUser() is None:
        return redirect("/login/")
    if session['userObj']['email'] == 'hidalgo@mit.edu' or session['userObj']['email'] == 'salesses@mit.edu' or session['userObj']['email'] == 'philsalesses@me.com':
        studies = Database.getStudiesAdmin()
    return auto_template('admin_all.html',studies=studies)
    
#--------------------Studies
@admin.route("/admin/studies/")
def view_studies():
    if getLoggedInUser() is None:
        return redirect("/login/")
    studies = Database.getStudies(session['userObj']['email'])
    return auto_template('admin_studies.html',studies=studies)
    
@admin.route("/admin/study/<study_id>/",methods = ['GET'])
def edit_studies(study_id):
    if getLoggedInUser() is None:
        return redirect("/login/")
    study = Database.getStudy(study_id)
    return auto_template('admin_study.html',study=study,study_id=study_id)
    
@admin.route('/admin/study/update/<study_id>/',methods=['POST'])
def update_study(study_id):
    study_name = request.form['study_name']
    study_question = request.form['study_question']
    study_public = request.form['study_public']
    Database.studies.update({'_id': Database.returnObjectId(study_id)}, { '$set': {'study_name' : study_name, 'study_question':study_question, 'study_public':study_public } }, True)    
    return jsonifyResponse({
    'success': True
    })

#--------------------Places
@admin.route("/admin/places/")
def view_places():
    if getLoggedInUser() is None:
        return redirect("/login/")
    places = [i for i in Database.getPlaces(session['userObj']['email'])]
    return auto_template('admin_places.html',places=places)
    
@admin.route("/admin/place/add/",methods = ['GET'])
def add_place_g():
    if getLoggedInUser() is None:
        return redirect("/login/")
    return auto_template('admin_place_add.html')
    
@admin.route("/admin/place/add/",methods = ['POST'])
def add_place_p():
    # Insert the new study into Mongo
    newPlaceID = Database.places.insert({
    'data_resolution': request.form['data_resolution'],
    'location_distribution': request.form['location_distribution'],
    'polygon': request.form['polygon'],
    'place_name': request.form['place_name'],
    'owner': session['userObj']['email']
    })
    return jsonifyResponse({
    'placeID': str(newPlaceID)
    })

@admin.route('/admin/place/populate/<place_id>/',methods=['GET'])
def admin_populate_place_g(place_id):
    place = Database.getPlace(place_id)
    return render_template('admin_place_populate.html',polygon=place['polygon'],place_id=place_id,locDist = place['location_distribution'], dataRes = place['data_resolution'])

@admin.route('/admin/place/populate/<place_id>/',methods=['POST'])
def admin_populate_place_p(place_id):
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

@admin.route("/admin/place/delete/<place_id>",methods = ['POST'])
def add_place_delete_p(place_id):
    # Insert the new study into Mongo
    placeDeleted = Database.deletePlace_Locations(place_id)
    return jsonifyResponse({
    'success': str(placeDeleted)
    })
    
@admin.route("/admin/study/delete/<study_id>",methods = ['POST'])
def study_delete_p(study_id):
    # Insert the new study into Mongo
    owner = session['userObj']['email']
    studyDeleted = Database.deleteStudy(study_id, owner)
    return jsonifyResponse({
    'success': str(studyDeleted)
    })
    
@admin.route("/admin/place/<place_id>/",methods = ['GET'])
def edit_places(place_id):
    if getLoggedInUser() is None:
        return redirect("/login/")
    place = Database.getPlace(place_id)
    return auto_template('admin_place.html',place=place)
    
@admin.route('/admin/place/update/<study_id>/',methods=['POST'])
def update_place(study_id):
    study_name = request.form['study_name']
    study_question = request.form['study_question']
    study_public = request.form['study_public']
    Database.studies.update({'_id': Database.returnObjectId(study_id)}, { '$set': {'study_name' : study_name, 'study_question':study_question, 'study_public':study_public } }, True)    
    return jsonifyResponse({
    'success': True
    })

#--------------------Locations
@admin.route("/admin/locations/",methods = ['GET'])
def admin_locations():
    if getLoggedInUser() is None:
        return redirect("/login/")
    owner = session['userObj']['email']
    locations = Database.getLocationsByOwner(owner)
    return auto_template('admin_locations.html',locations=locations)
    
@admin.route("/admin/locations/delete/<location_id>",methods = ['POST'])
def location_delete_p(location_id):
    # Insert the new study into Mongo
    locationDeleted = Database.deleteLocation(location_id)
    return jsonifyResponse({
    'success': str(locationDeleted)
    })

@admin.route('/admin/locations/curate/<place_id>/',methods=['GET'])
def curate_study(place_id):
    place = Database.getPlace(place_id)
    locations = [i for i in Database.getLocations(place_id)]
    return auto_template('admin_locations_curate.html',polygon=place['polygon'],locations=locations,place_id=place_id)

#--------------------Images
@admin.route("/admin/images/",methods = ['GET'])
def admin_images():
    if getLoggedInUser() is None:
        return redirect("/login/")

    return auto_template('admin_images.html')
#--------------------Votes
@admin.route("/admin/votes/",methods = ['GET'])
def admin_votes():
    if getLoggedInUser() is None:
        return redirect("/login/")

    return auto_template('admin_votes.html')

#--------------------Results
@admin.route("/admin/results/",methods = ['GET'])
def admin_results():
    if getLoggedInUser() is None:
        return redirect("/login/")

    return auto_template('admin_results.html')