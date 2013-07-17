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

@root.route("/vision/")
def load_vision():
  votesCount = Database.getVotesCount()
  return auto_template('vision.html', votes_contributed=votesCount)

@root.route("/data/")
def load_data():
  votesCount = Database.getVotesCount()
  return auto_template('datasets.html', votes_contributed=votesCount)

@root.route("/rankings/")
def load_rankings():
  votesCount = Database.getVotesCount()
  return auto_template('rankings.html', votes_contributed=votesCount)

@root.route("/experiments/")
def load_experiments():
  votesCount = Database.getVotesCount()
  return auto_template('experiments.html', votes_contributed=votesCount)

@root.route("/papers/")
def load_papers():
  votesCount = Database.getVotesCount()
  return auto_template('papers.html', votes_contributed=votesCount)

@root.route("/another/<study_id>")
def load_another_study(study_id):
  studyObj = Database.getAnotherStudy(study_id)
  votesCount = Database.getVotesCount()
  return auto_template('main.html',study_id=studyObj.get('_id'),study_prompt=studyObj.get('study_question'), votes_contributed=votesCount)
