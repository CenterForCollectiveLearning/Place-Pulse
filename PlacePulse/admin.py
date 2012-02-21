from flask import Module
from flask import redirect,render_template,request

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

#--------------------Places
@admin.route('/admin/aggregate_studies/<study_id>',methods = ['POST'])
def updateCities(study_id):
    if getLoggedInUser() is None:
        return redirect("/login/")
    cityname = request.form['city']
    Database.studies.update({'_id':Database.returnObjectId(study_id)},{'$set': {'city':cityname}})
    return jsonifyResponse({
        'success':True
    })

def classifyStudy(study_id):
    if getLoggedInUser() is None:
        return redirect("/login/")
    study = Database.getStudy(study_id)
    cities=''
    for city in Database.studies.distinct('city'):
        if(len(str(city))>0):
            cities+=str(city)+','
    cities=cities[:-1]
    return auto_template('admin.html',study_id=study_id,polygon=study['polygon'],cities=cities)

#--------------------Locations

#--------------------Images

#--------------------Votes
@admin.route("/admin/votes/<study_id>/",methods=['GET'])
def calculate_ranking(study_id):
    votes = Database.getVotes(study_id)
    return auto_template('view_votes.html',votes=votes)

#--------------------Results