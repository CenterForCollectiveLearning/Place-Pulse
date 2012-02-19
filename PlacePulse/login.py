import json
import urllib2,urllib

from flask import Module
from flask import redirect,render_template,request,session

from util import *

login = Module(__name__)

@login.route("/login/browserid/",methods=['POST'])
def handle_browserid():
    data = {
        "assertion" : request.form.get('assertion'),
        "audience" : urllib2.Request(request.url).get_host()
    }        
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
            'success': True
        })
    except:
        return jsonifyResponse({
            'success': False,
            'error': True,
            'error_description': 'BrowserID assertion check failed!'
        })

@login.route("/logout/")
def logout():
    del session['userObj']
    return redirect('/')