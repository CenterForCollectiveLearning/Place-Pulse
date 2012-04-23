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
    popular_studies = Database.getPopularStudies(5)
    new_cities = Database.getNewCities(5)
    inactive_studies = Database.getInactiveStudies(5)
    return auto_template('admin.html',popular_studies=popular_studies,new_cities=new_cities,inactive_studies=inactive_studies)
    
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
def add_places():
    if getLoggedInUser() is None:
        return redirect("/login/")
    return auto_template('admin_add_place.html')
    
@admin.route("/admin/place/add/",methods = ['POST'])
def add_place():
    # Insert the new study into Mongo
    newPlaceID = Database.places.insert({
    'data_resolution': request.form['data_resolution'],
    'location_distribution': request.form['location_distribution'],
    'polygon': request.form['polygon'],
    'place_name': request.form['place_name'],
    'owner': session['userObj']['email']
    })
    return jsonifyResponse({
    'success': True
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

#--------------------Images

#--------------------Votes
@admin.route("/admin/votes/<study_id>/",methods=['GET'])
def calculate_ranking(study_id):
    votes = Database.getVotes(study_id)
    return auto_template('view_votes.html',votes=votes)

#--------------------Results