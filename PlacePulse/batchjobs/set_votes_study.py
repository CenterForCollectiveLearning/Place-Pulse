__author__ = 'Daniel Smilkov (dsmilkov@gmail.com)'

import sys, os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from db import Database

for study in Database.studies.find():
    studyid = str(study['_id'])
    nvotes = 0
    for vote in Database.votes.find():
        if vote['study_id'] == studyid: nvotes+=1        
    print study['study_name'], nvotes
    Database.studies.update({'_id': study['_id']}, { '$set' : { 'num_votes': nvotes }})
        