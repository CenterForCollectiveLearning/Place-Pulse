import json
import os
import urllib2,urllib

from flask import Module
from flask import redirect,request,session,url_for
from flaskext.oauth import OAuth

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
    session['userObj'] = {
        'source': 'facebook',
        'name':  me.data['name'],
        'email': me.data['email']
    }
    return redirect(request.args.get('next') or '/')

@login.route("/login/browserid/",methods=['POST'])
def handle_browserid():
    data = {
        "assertion" : request.form.get('assertion'),
        "audience" : urllib2.Request(request.url).get_host()
    }
    nextURL = request.args.get('next') or '/'
    try:
        req = urllib2.Request('https://browserid.org/verify',urllib.urlencode(data))        
        json_result = urllib2.urlopen(req).read()
        
        # Parse the JSON to extract the e-mail
        result = json.loads(json_result)
        session['userObj'] = {
            'source': 'browserid',
            'email':  result.get('email')
        }
        return jsonifyResponse({
            'success': True,
            'next': nextURL
        })
    except:
        return jsonifyResponse({
            'success': False,
            'error': True,
            'error_description': 'BrowserID assertion check failed!'
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
    if getLoggedInUser():
        del session['userObj']
    return redirect(request.args.get('next') or '/')
