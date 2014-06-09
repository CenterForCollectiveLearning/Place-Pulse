import sys, os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from db import Database

count = 0
for vote in Database.votes.find():
  study_id = vote['study_id']
  if vote['choice'] == 'equal':
    a_qs = Database.getQS(study_id, vote['left'])
    b_qs = Database.getQS(study_id, vote['right'])
    if 'active' not in a_qs and 'active' not in b_qs: # if both images are active, make one inactive
      a_nvotes = a_qs['num_votes']
      b_nvotes = b_qs['num_votes']
      if a_nvotes > b_nvotes: # make B inactive
        Database.qs.update({'_id': b_qs['_id']}, {'$set': { 'active': 0, 'equal_to': a_qs['_id']}})
      else: # make A inactive
        Database.qs.update({'_id': a_qs['_id']}, {'$set': { 'active': 0, 'equal_to': b_qs['_id']}})
  count += 1
  if count % 1000 == 0: print count