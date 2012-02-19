import os

from PlacePulse import app

from flask import render_template,session

import json

class Buckets:
    Unknown, Queue, Archive = range(3)
    QueueSize = 100

# Calls render_template with default template variables included
def auto_template(template_name, **kwargs):
    userObj = getLoggedInUser()
    extraObj = {
        'userObj': userObj
    }
    kwargs.update(extraObj)
    return render_template(template_name, **kwargs)

def getFBLoginLink():
    FB_APP_ID = '112177295578109'
    FB_LOGIN_LINK = "https://www.facebook.com/dialog/oauth?scope=email,user_education_history,offline_access,user_likes&client_id=%s&redirect_uri=%s/login/fromfb/" % (FB_APP_ID, os.environ['PLACEPULSE_BASEURL'])
    return FB_LOGIN_LINK

def getLoggedInUser():
    return session.get('userObj')

def jsonifyResponse(obj):
    resp = app.make_response(json.dumps(obj))
    resp.mimetype = 'application/json'
    return resp

def objifyPlace(place):
    return {
        'id' : str(place['_id']),
        'loc' : place['loc']
    }