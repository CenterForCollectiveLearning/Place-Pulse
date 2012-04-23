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
    studies = Database.getStudies()
    return auto_template('admin_studies.html',studies=studies)
    
@admin.route("/admin/study/<study_id>",methods = ['GET'])
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
def view_placess():
    if getLoggedInUser() is None:
        return redirect("/login/")
    studies = Database.getStudies()
    return auto_template('admin_places.html',studies=studies)
    
@admin.route("/admin/place/<study_id>",methods = ['GET'])
def edit_places(study_id):
    if getLoggedInUser() is None:
        return redirect("/login/")
    study = Database.getStudy(study_id)
    return auto_template('admin_place.html',study=study,study_id=study_id)
    
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