import json
import os
import urllib2,urllib

from flask import Module
from flask import redirect,request,session,url_for
from flaskext.oauth import OAuth

from db import Database
from util import *

login = Module(__name__)
oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=os.environ['FACEBOOK_APP_ID'],
    consumer_secret=os.environ['FACEBOOK_APP_SECRET'],
    request_token_params={'scope': 'email,user_likes,friends_likes,user_location'}
)

def cookieUser(email,extra_data=None):
    if extra_data is None:
        extra_data = dict()
    userObjData =  {
        'email':  email
    }
    userObjData.update(extra_data)
    def saveAndSet(_userObj):
        Database.users.save(_userObj)
        session['userObj'] = _userObj
    # TODO: Find out why session['userObj'] sometimes persists after logout
    # if session.get('userObj'):
    #     print "session.get('userObj'):"
    #     userObjData.update(session['userObj'])
    #     saveAndSet(userObjData)
    #     #Database.createUserObj(email=email,voterID=session['userObj'].get('voter_uniqueid'),extra_data=extra_data)
    # else:
    # Look for existing userObjs for this e-mail or a user's voterID
    emailUserObj = Database.getUserByEmail(email)
    voterIDUserObj = Database.getUserByVoterID(session['voterID']) if session.get('voterID') else None
    
    if voterIDUserObj:
        if emailUserObj:
            if emailUserObj.get('voter_uniqueid'):
                session['userObj'] = emailUserObj
            else:
                emailUserObj['voter_uniqueid'] = session['voterID']
                saveAndSet(emailUserObj)
        else:
            voterIDUserObj['email'] = email
            saveAndSet(voterIDUserObj)
    elif emailUserObj:
        if not(emailUserObj.get('voter_uniqueid')) and session.get('voterID'):
           emailUserObj['voter_uniqueid'] = session.get('voterID')
           saveAndSet(emailUserObj)
        else:
            session['userObj'] = emailUserObj
    else:
        session['userObj'] = Database.createUserObj(voterID=session.get('voterID'),email=email,extra_data=extra_data)           

@login.route('/login/facebook/')
def handle_facebook():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))
        
@login.route('/login/facebook_authorized/')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me')
    if me.data.get('error'):
        return 'Could not call Facebook.'
    userObjData = {
        'name':  me.data['name'],
        'email': me.data['email'],
        'source': 'facebook',
        'facebook_id': me.data['id']
    }
    cookieUser(me.data['email'],userObjData)
    # if session.get('voterID'): associateEmailWithVoterID(me.data['email'],session.get('voterID'))
    return redirect(request.args.get('next') or '/')

@login.route("/login/browserid/",methods=['POST'])
def handle_browserid():
    data = {
        "assertion" : request.form.get('assertion'),
        "audience" : urllib2.Request(request.url).get_host()
    }
    nextURL = request.args.get('next') or '/'
    req = urllib2.Request('https://browserid.org/verify',urllib.urlencode(data))
    json_result = urllib2.urlopen(req).read()
    # Parse the JSON to extract the e-mail
    result = json.loads(json_result)
    if result.get('status') == 'failure':
        return jsonifyResponse({
            'success': False,
            'error': True,
            'error_description': 'BrowserID assertion check failed!'
        })
    userObjData = {
        'source': 'browserid',
    }
    cookieUser(result.get('email'),userObjData)
    # if session.get('voterID'): associateEmailWithVoterID(result.get('email'),session.get('voterID'))
    # upsertUser(result.get('email'))
    return jsonifyResponse({
        'success': True,
        'next': nextURL
    })
        
@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

@login.route("/login/")
def signin():
    if getLoggedInUser() is not None:
        return redirect("/")
    fbLoginLink = url_for('login.handle_facebook',next=request.args.get('next') or '/')
    browserIDLoginLink = url_for('login.handle_browserid',next=request.args.get('next') or '/')
    return auto_template('login.html',fb_login_link=fbLoginLink,browserid_login_link=browserIDLoginLink)

@login.route("/logout/")
def logout():
    if session.get('userObj'):
        del session['userObj']
    if session.get('voterID'):
        del session['voterID']
    session.modified = True
    return redirect(request.args.get('next') or '/')
