from flask import Module

from flask import redirect,render_template,request,session,url_for

from util import *

matching = Module(__name__)

def getNewPrompt():
    return {
        "locs": [
            {
                "id": "1",
                "coords": [40.7321,-73.9924]
            },
            {
                "id": "2",
                "coords": [48.8591,2.3153]
            },
            {
                "id": "3",
                "coords": [51.517,-0.127]
            },
            {
                "id": "4",
                "coords": [34.090,-118.359]
            }
        ],
        "place_names": [
            {
                "name_str": "Paris"
            },
            {
                "name_str": "NYC"
            },
            {
                "name_str": "London"
            },
            {
                "name_str": "Los Angeles"
            },
        ]
    }

#--------------------Main
@matching.route("/matching/")
def serve_matching_page():
    return auto_template('matching.html')
    
@matching.route("/matching/get_prompt/")
def get_matching_prompt():
    return jsonifyResponse(getNewPrompt())
    return auto_template('matching.html')

@matching.route("/matching/eval_solution/",methods=['POST'])
def eval_matching_solution():
    from random import randint
    return jsonifyResponse({
        "num_correct": randint(0,4),
        "next_prompt": getNewPrompt()
    })