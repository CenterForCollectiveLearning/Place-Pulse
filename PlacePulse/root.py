from flask import Module
from flask import redirect,request

from random import sample
from util import *

root = Module(__name__)

from db import Database

@root.route("/about/")
def load_about():
	return auto_template('about.html')

@root.route("/data/")
def load_data():
	return auto_template('data.html')

@root.route("/faq/")
def load_faq():
	return auto_template('faq.html')

@root.route("/contact/")
def load_contact():
	return auto_template('contact.html')
