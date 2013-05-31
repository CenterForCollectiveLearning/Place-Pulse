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
