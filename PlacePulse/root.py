from flask import Module
from flask import redirect,render_template,request

from random import sample
from util import *

root = Module(__name__)

from db import Database

@root.route("/about/")
def load_about():
	return auto_template('about.html')