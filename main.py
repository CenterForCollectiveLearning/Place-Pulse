import os
import logging
from flask import Flask,render_template,request

from db import Database

import json

app = Flask(__name__)

def jsonifyResponse(obj):
    resp = app.make_response(json.dumps(obj))
    resp.mimetype = 'application/json'
    return resp

@app.route("/")
def main():
    return render_template('main.html')

@app.route("/study/view/<study_id>",methods=['GET'])
def server_view_study(study_id):
    return render_template('view_study.html',study_id=study_id)

@app.route("/study/create")
def serve_create_study():
    return render_template('create_study.html')
    
@app.route('/study/create',methods=['POST'])
def create_study():    
    # Insert the new study into Mongo
    newStudyID = Database.studies.insert({
        'question': request.form['question'],
        'maxVotes': request.form['maxVotes'],
        'polygon': request.form['polygon']})
    # Return the ID for the client to rendezvous at /study/populate/<id>
    return jsonifyResponse({
        'studyID': str(newStudyID)
    })

@app.route('/study/populate/<study_id>',methods=['GET'])
def serve_populate_study(study_id):
    study = Database.getStudy(study_id)
    return render_template('populate_study.html',polygon=study['polygon'],study_id=study_id)

@app.route('/study/populate/<study_id>',methods=['POST'])
def populate_study(study_id):
    Database.places.insert({
        'loc': [request.form['lat'],request.form['lng']],
        'study_id': request.form['study_id']
    })
    return jsonifyResponse({
        'success': True
    })
    
def buildIndices():
    # Build spatial index
    Database.places.ensureIndex({
        'loc': '2d'
    })

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.logger.setLevel(logging.DEBUG)
    app.config.update(DEBUG=True,PROPAGATE_EXCEPTIONS=True,TESTING=True)
    app.run(debug=True,host='0.0.0.0',port=port)