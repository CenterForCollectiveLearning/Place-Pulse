__author__ = 'Daniel Smilkov (dsmilkov@gmail.com)'

import sys, os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
import pymongo
from db import Database


'''The old version of the db doesn't create a qs entry when a study is created.
Because of this, selecting a random pair of images doesn't work correctly
'''

def insert_qs():
  Database.db.drop_collection(Database.qs)
  Database.db.drop_collection(Database.db.qs_place)
  # drop index for fast insertion
  Database.qs.drop_indexes()
  Database.qs.ensure_index("_id")
  Database.db.qs_place.drop_indexes()
  Database.db.qs_place.ensure_index("_id")
  
  studies = Database.studies.find()
  print studies.count(), 'studies found in the db'
  for i, study in enumerate(studies):
    study_id = str(study['_id'])
    places_ids = study['places_id']
    # NOTE: places_ids are objectids, we need strings
    places_ids = [str(place) for place in places_ids]
    
    # add a score for each location in the given study
    for place_id in places_ids:
      Database._add_qs_place(place_id, study_id)


    #find all the locations used by this study and update/create qs entries
    locations = Database.locations.find({'place_id' : {'$in' : places_ids}})
    # update/create a qs field for every study, location pair
    print 'processing study', i+1, study['study_name'], 'with', locations.count(), 'locations from', len(places_ids), 'places'
    ninserts = 0
    for loc in locations:
      place_id = str(loc['place_id'])
      location_id = str(loc['_id'])
      result = Database._add_qs(location_id, place_id, study_id)
      ninserts += 1
    print 'finished processing study', study['study_name'], 'ninserts:', ninserts


def transition_votes():
  votes = Database.votes.find()
  print votes.count(), 'votes found in the db'
  nremoved = 0
  old2new_studyid = { '50a68a51fdc9f05596000002' : '50a68a51fdc9f05596000002', # safer
                              '50f62ae5a84ea7c5fdd2e451' : '50f62c68a84ea7c5fdd2e456', # cleaner
                              '50f62cb7a84ea7c5fdd2e458' : '50f62cb7a84ea7c5fdd2e458', # wealthier
                              '50f62b33a84ea7c5fdd2e452' : '50f62ccfa84ea7c5fdd2e459', # more depressing
                            }
  for vote in votes:
    if vote['study_id'] not in old2new_studyid or Database.getLocation(vote['left']) is None \
                                          or Database.getLocation(vote['right']) is None:
      Database.votes.remove({'_id': vote['_id']})
      nremoved+=1
    else:
      vote['study_id'] = old2new_studyid[vote['study_id']]
      Database.votes.update({'_id': vote['_id']}, vote)
  print nremoved, 'invalid votes removed from the db'


def process_past_votes():
  print 'start processing past votes'
  Database.qs.ensure_index([  ('study_id', pymongo.ASCENDING), ('location_id', pymongo.ASCENDING)]) # for updating the q scores of the two images after every vote 
  Database.db.qs_place.ensure_index([('study_id', pymongo.ASCENDING), ('place_id', pymongo.ASCENDING)]) # for updating the q scores of the places after every vote 
  Database.locations.ensure_index("place_id")
  votes = Database.votes.find()
  print votes.count(), 'votes found in the db'
  for vote in votes:
    study_id = str(vote['study_id'])
    if vote['choice'] in ['left', 'equal']:
      winner_locid = vote['left']
      loser_locid = vote['right']
    else:
      winner_locid = vote['right']
      loser_locid = vote['left']
    isDraw = vote['choice'] == 'equal'
    Database.updateQScores(study_id, winner_locid, loser_locid, isDraw)
  print 'done processing votes'



def count_scores():
  qss = Database.qs.find()
  print 'total q scores', qss.count()
  nmus, nstds = 0,0
  for qs in qss:
    #print qs['trueskill']['score']
    nmus += len(qs['trueskill']['mus'])
    nstds += len(qs['trueskill']['stds'])
  print nmus, nstds


insert_qs()
transition_votes()
process_past_votes()