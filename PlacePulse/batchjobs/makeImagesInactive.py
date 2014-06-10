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
    a_nvotes = a_qs['num_votes']
    b_nvotes = b_qs['num_votes']
      
    if 'active' not in a_qs: # if A is still active
      # if A has less votes then B, and B doesn't point back to A
      if a_nvotes < b_nvotes and ('equal_to' not in b_qs or b_qs['equal_to'] != a_qs['_id']):
        Database.qs.update({'_id': a_qs['_id']}, {'$set': { 'active': 0, 'equal_to': b_qs['_id']}})

    if 'active' not in b_qs: # if B is still active
      # if B has less votes then A, and A doesn't point back to B
      if a_nvotes > b_nvotes and ('equal_to' not in a_qs or a_qs['equal_to'] != b_qs['_id']):
        Database.qs.update({'_id': b_qs['_id']}, {'$set': { 'active': 0, 'equal_to': a_qs['_id']}})
  count += 1
  if count % 1000 == 0: print count