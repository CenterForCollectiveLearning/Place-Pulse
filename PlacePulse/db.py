import os
import pymongo
import random
import sys
from uuid import uuid4
from bson.objectid import ObjectId
from pymongo import ASCENDING
import math
from random import choice
from random import randint
from trueskill import trueskill

# FIXME: We can't get away with silencing all errors in these methods.
# They've made too many bugs hard to find. Let's add a real error logging system.

class database(object):
#--------------------Results
    def getResultsForStudy(self,studyID):
        # FIXME: Normalize use of ObjectId/str for _id's.
        return self.results.find_one({
                "$or":[
                    {'study_id': studyID},
                    {'study_id': ObjectId(studyID)}
                ]
        })
#--------------------Studies
    def getStudy(self,study_id):
        return self.studies.find_one(ObjectId(study_id))

    # Study objects can get very large (see places_id), so this func just returns the title
    def getStudyQuestion(self,study_id):
        return self.studies.find_one(ObjectId(study_id),{"study_question":1})['study_question']

    def getRandomStudy(self):
        count = self.studies.count()
        randomNumber = random.randint(0,count-1)
        return self.studies.find().limit(-1).skip(randomNumber).next()

    def getAnotherStudy(self,study_id):
        count = self.studies.count()
        randomNumber = random.randint(0,count-2)
        return self.studies.find({'_id':{'$ne':ObjectId(study_id)}}).limit(-1).skip(randomNumber).next()

    def deleteStudy(self,study_id, owner):
        study_query = { '_id' : ObjectId(study_id), 'owner': owner }
        self.studies.remove(study_query)
        # delete all the qs entries from that study
        self.qs.remove({'study_id': study_id})
        return True

    def deleteStudyAdmin(self,study_id):
        self.studies.remove( { '_id' : ObjectId(study_id)})
        # delete all the qs entries from that study
        self.qs.remove({'study_id': study_id})
        return True

    def returnObjectId(self,study_id):
        return ObjectId(study_id)

    def getStudies(self,owner):
        return self.studies.find({'owner':owner})

    def getStudiesAdmin(self):
        return self.studies.find({}, {'places_id': 0})

    def getNewStudies(self,limit):
        return self.studies.find().limit(limit)

    def getPopularStudies(self,limit):
        return self.studies.find().limit(limit)

    def getInactiveStudies(self,limit):
        return self.studies.find().limit(limit) #Need to add votes_needed field for studies to track how long they have to go.

#--------------------Places
    def getPlaces(self):
        return self.places.find()

    def getPlace(self,place_id):
        return self.places.find_one(ObjectId(place_id))

    def deletePlace_Locations(self,place_id):
        self.places.remove( { '_id' : ObjectId(place_id) })
        self.locations.remove( { 'place_id' : str(place_id) })
        return True

    def getNewCities(self,limit):
        return self.studies.find().limit(limit)

#--------------------Locations
    def getLocations(self,place_id,limit=96):
        return self.locations.find({'place_id': place_id}).limit(limit)

    def getLocationsByOwner(self,owner):
        return self.locations.find({'owner': owner})

    def getLocation(self,location_id):
        return self.locations.find_one(ObjectId(location_id))

    def updateLocation(self,location_id,heading,pitch):
        self.locations.update( { '_id' : ObjectId(location_id) } , { '$set' : { 'heading' : heading, 'pitch' : pitch } } )
        return True

    def deleteLocation(self,location_id):
        self.locations.remove( { '_id' : ObjectId(location_id) })
        return True

    def getRandomLocationByPlace(self,place_id):
        if isinstance(place_id,ObjectId):
            place_id = str(place_id)
        placeCount = Database.locations.find({"places_id": place_id}).count()
        if placeCount == 0: return None
        return self.locations.find().limit(-1).skip(randint(0,placeCount-1)).next()

#--------------------Users

    def getUserById(self,userID):
        return self.users.find_one({
            '_id': userID if isinstance(userID,ObjectId) else ObjectId(userID)
        })

    def getUserByEmail(self,email):
        return self.users.find_one({
            'email': email
        })

    def getUserByVoterID(self,voterID):
        return self.users.find_one({
            'voter_uniqueid': voterID
        })

    def add_place(self, data_resolution, location_distribution, polygon, place_name, owner):
        return Database.places.insert({
        'data_resolution': data_resolution,
        'location_distribution': location_distribution,
        'polygon': polygon,
        'place_name': place_name,
        'owner': owner,
        })


    # should be called internally, when adding a new location to a place for a given study
    def _add_qs(self, location_id, place_id, study_id):
        return Database.qs.insert({
            'location_id': str(location_id),
            'study_id': str(study_id),
            'place_id': str(place_id),
            'num_votes':0,
            'random':random.random(),
            'trueskill': {
              'score':trueskill.get_score(trueskill.mu0, trueskill.std0),
              'mus':[trueskill.mu0],
              'stds':[trueskill.std0]
            }
        })

    # should be called internally, when adding a new location to a place for a given study
    def _add_qs_place(self, place_id, study_id):
        return self.db.qs_place.insert({
            'place_id': str(place_id),
            'study_id': str(study_id),
            'trueskill': {
              'score':trueskill.get_score(trueskill.mu0, trueskill.std0),
              'mus':[trueskill.mu0],
              'stds':[trueskill.std0]
            }
        })

    def get_qs_place(self, place_id, study_id):
        return self.db.qs_place.find_one({'place_id': str(place_id),'study_id': str(study_id)})

    def add_location(self, lat, lng, place_id, owner, study_id):
        ''' Adding the location consists of several tasks:
            1. create/update the score for the place for the current study
            2. add the new location
            3. add score for the location for the current study
        '''

        # 1. add/update score for the place
        qs_place = self.get_qs_place(place_id, study_id)
        if qs_place is None:
            self._add_qs_place(place_id, study_id)
        else:
            # update the score of a place accordingly (qs_entry)
            # get the old scores
            mus = qs_place['trueskill']['mus']
            stds = qs_place['trueskill']['stds']
            old_mu = mus[-1]
            old_std = stds[-1]

            # count how many locations are already from that place
            N = Database.locations.find({'place_id': str(place_id)}).count()
            # compute the new scores
            new_mu = float(old_mu * N + trueskill.mu0)/(N+1)
            mus[-1] = new_mu
            new_std = math.sqrt(old_std**2 * N**2 + trueskill.std0**2)/(N+1)
            stds[-1] = new_std
            new_score = trueskill.get_score(new_mu, new_std)

            # finally, update the qs_place entry
            self.db.qs_place.update({'place_id': str(place_id), 'study_id': str(study_id)}, {
                '$set': { 'trueskill.score': new_score,
                        'trueskill.mus' : mus,
                        'trueskill.stds': stds
                }

            })
        # 2. add the new location
        locID = Database.locations.insert({
           'loc': [lat, lng],
           'type':'gsv',
           'place_id': str(place_id),
           'owner': owner, #TODO: REAL LOGIN SECURITY
           'heading': 0,
           'pitch': 0,
           'votes':0
        })
        # 3. add score for the location
        self._add_qs(str(locID), place_id, study_id)
        return locID


    def createUserObj(self,voterID=None,email=None,extra_data=None):
        if voterID is None:
            voterID = str(uuid4().hex)
        userObj = {
            "voter_uniqueid": voterID
        }
        if email is not None:
            userObj['email'] = email
        if extra_data is not None:
            userObj.update(extra_data)
        newID = self.users.insert(userObj)
        userObj['_id'] = newID
        return userObj
#--------------------Votes
    def getVotes(self,study_id):
        # FIXME: Normalize use of ObjectId/str for _id's.
        return self.votes.find({
                "$or":[
                    {'study_id': study_id},
                    {'study_id': ObjectId(study_id)}
                ]
        })

    def getVotesCount(self, study_id=None):
        if study_id is not None:
            return self.votes.find({"study_id": study_id}).count()
        else:
            return self.votes.find().count()

#--------------------QS
    def getQS(self,study_id, location_id):
        return self.qs.find_one({
                "study_id": str(study_id),
                "location_id": str(location_id)
            })


    # should be called internally, when update the qs scores of locations/places after a vote
    def _pushQscore(self, qs_row_loc, mu_loc, std_loc, old_mu_loc, old_std_loc):
        # update qs entry for the location
        score = trueskill.get_score(mu_loc, std_loc)
        self.qs.update({'_id': qs_row_loc['_id']}, {
            '$set': { 'trueskill.score': score},
            '$inc' : { 'num_votes': 1 },
            '$push' : { 'trueskill.mus' : mu_loc, 'trueskill.stds': std_loc }

        })
        # update the qs entry for the place where the location is from
        place_id = qs_row_loc['place_id']
        study_id = qs_row_loc['study_id']
        qs_place = self.get_qs_place(place_id, study_id)
        if qs_place == None:
            print "Couldn't find qs_place row with place_id", place_id, "and study_id", study_id
            return
        # update the score of a place accordingly (qs_entry)
        # get the old scores
        old_mu = qs_place['trueskill']['mus'][-1]
        old_std = qs_place['trueskill']['stds'][-1]
        # count how many locations are already from that place
        N = Database.locations.find({'place_id': str(place_id)}).count()
        # compute the new score
        new_mu = old_mu + float(mu_loc - old_mu_loc)/N
        new_std = math.sqrt( old_std**2 + (std_loc**2 - old_std_loc**2)/N**2 )
        score = trueskill.get_score(new_mu, new_std)
        self.db.qs_place.update({'_id': qs_place['_id']}, {
            '$set': { 'trueskill.score': score},
            '$inc' : { 'num_votes': 1 },
            '$push' : { 'trueskill.mus' : new_mu, 'trueskill.stds': new_std }

        })

    def updateQScores(self, study_id, winner_locid, loser_locid, isDraw):
        ''' Update Q scores consists of several tasks:
            1. update the scores of the two locations
            2. update the scores of the place/two places where these two locations are from
        '''
        # 1. update the scores of the two locations (images)
        winner_qs = self.getQS(study_id, winner_locid)
        loser_qs = self.getQS(study_id, loser_locid)
        if winner_qs is None:
            print "Couldn't find a qs row with study_id", study_id, "and location id", winner_locid
            return
        if loser_qs is None:
            print "Couldn't find a qs row with study_id", study_id, "and location id", loser_locid
            return
        # get the last mu and standard deviation
        old_mu_winner = winner_qs['trueskill']['mus'][-1]
        old_std_winner = winner_qs['trueskill']['stds'][-1]
        old_mu_loser = loser_qs['trueskill']['mus'][-1]
        old_std_loser = loser_qs['trueskill']['stds'][-1]
        # update scores using the trueskill update equations
        (mu_winner, std_winner), (mu_loser, std_loser) = trueskill.update_rating((old_mu_winner, old_std_winner), (old_mu_loser, old_std_loser), isDraw)
        # 2. push and scores of the locations to the db and update the scores of the places where these locations are from
        self._pushQscore(winner_qs, mu_winner, std_winner, old_mu_winner, old_std_winner)
        self._pushQscore(loser_qs, mu_loser, std_loser, old_mu_loser, old_std_loser)
        return True

    def randomQS(self, study_id, exclude=None):
      rand = random.random()
      query = { 'study_id' : study_id, 'random' : { '$gte' : rand}}
      qs = Database.qs.find_one( query )
      if qs is None:
        query['random'] = { '$lte' : rand}
        qs = Database.qs.find_one(query)
      if exclude and qs["location_id"] == exclude: return Database.randomQS(study_id, exclude)
      return qs

    @property
    def locations(self):
        return self.db.locations

    @property
    def places(self):
        return self.db.places

    @property
    def results(self):
        return self.db.results

    @property
    def studies(self):
        return self.db.studies

    @property
    def users(self):
        return self.db.pp_users

    @property
    def votes(self):
        return self.db.votes

    @property
    def voterids(self):
        return self.db.voterids

    @property
    def qs(self):
        return self.db.qs

    @property
    def qs_place(self):
        return self.db.qs_place

    @property
    def db(self):
        if not hasattr(self, '_db'):
            dbName = os.environ.get('MONGO_DBNAME', 'placepulse')
            self._db = self.conn[dbName]
            if os.environ.get('MONGO_USER') and os.environ.get('MONGO_PASSWORD'):
                self._db.authenticate(os.environ['MONGO_USER'],os.environ['MONGO_PASSWORD'])
        return self._db

    @property
    def conn(self):
        if not hasattr(self, '_conn'):
            if os.environ.get('MONGO_HOSTNAME') and os.environ.get('MONGO_PORT'):
                self._conn = pymongo.Connection(os.environ.get('MONGO_HOSTNAME'), port=int(os.environ.get('MONGO_PORT')))
            else: self._conn = pymongo.Connection()
        return self._conn

# a singleton object
Database = database()
