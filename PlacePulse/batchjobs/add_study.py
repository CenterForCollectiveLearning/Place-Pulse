__author__ = 'Daniel Smilkov (dsmilkov@gmail.com)'

import sys, os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from db import Database

question = sys.argv[1]
study = Database.studies.find_one()
del study['_id']
study['study_name'] = question
study['study_question'] = question
study_id = str(Database.studies.insert(study))

places_ids = study['places_id']
# NOTE: places_ids are objectids, we need strings
places_ids = [str(place) for place in places_ids]

# add a score for each location in the given study
for place_id in places_ids:
  Database._add_qs_place(place_id, study_id)


#find all the locations used by this study and update/create qs entries
locations = Database.locations.find({'place_id' : {'$in' : places_ids}})
# update/create a qs field for every study, location pair
print 'adding study', study['study_name'], 'with', locations.count(), 'locations from', len(places_ids), 'places'
ninserts = 0
for loc in locations:
  place_id = str(loc['place_id'])
  location_id = str(loc['_id'])
  result = Database._add_qs(location_id, place_id, study_id)
  ninserts += 1
print 'finished processing study', study['study_name'], 'ninserts:', ninserts
