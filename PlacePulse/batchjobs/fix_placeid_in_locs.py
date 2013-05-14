import sys, os
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.dirname(CURRENT_DIR))
from db import Database

''' Every location row has an array of place_id of length 1.
   This update converts that array of only one string, to string
'''

for loc in Database.locations.find():
  Database.locations.update(loc, {"$set":{ 'place_id': loc['place_id'][0]}})