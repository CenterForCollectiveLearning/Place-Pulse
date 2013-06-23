from flask import Module
from flask import redirect,request

from random import sample
from util import *

root = Module(__name__)

from db import Database

@root.route("/about/")
def load_about():
  votesCount = Database.getVotesCount()
  return auto_template('about.html', votes_contributed=votesCount)

@root.route("/ongoing/")
def load_ongoing():
  votesCount = Database.getVotesCount()
  return auto_template('ongoing.html', votes_contributed=votesCount)

@root.route("/data/")
def load_data():
  votesCount = Database.getVotesCount()
  return auto_template('data.html', votes_contributed=votesCount)

@root.route("/results/")
def load_faq():
  votesCount = Database.getVotesCount()
  return auto_template('results_landing.html', votes_contributed=votesCount)

@root.route("/contact/")
def load_contact():
  votesCount = Database.getVotesCount()
  return auto_template('contact.html', votes_contributed=votesCount)

@root.route("/another/<study_id>")
def load_another_study(study_id):
  studyObj = Database.getAnotherStudy(study_id)
  votesCount = Database.getVotesCount()
  return auto_template('main.html',study_id=studyObj.get('_id'),study_prompt=studyObj.get('study_question'), votes_contributed=votesCount)
