import os
import pymongo
import random
import sys
from uuid import uuid4
from bson.objectid import ObjectId
from pymongo import ASCENDING

from random import choice
from random import randint

# FIXME: We can't get away with silencing all errors in these methods.
# They've made too many bugs hard to find. Let's add a real error logging system.

class database(object):
#--------------------Results
    def getResultsForStudy(self,studyID):
        # FIXME: Normalize use of ObjectId/str for _id's.
        try:
            return self.results.find_one({
                "$or":[
                    {'study_id': studyID},
                    {'study_id': ObjectId(studyID)}
                ]
            })
        except:
            return None

#--------------------Studies
    def getStudy(self,study_id):
        try:
            return self.studies.find_one(ObjectId(study_id))
        except:
            return None
    
    # Study objects can get very large (see places_id), so this func just returns the title
    def getStudyQuestion(self,study_id):
        try:
            return self.studies.find_one(ObjectId(study_id),{"study_question":1})['study_question']
        except:
            return None
            
    def getRandomStudy(self):
        try:
            count = self.studies.count()
            randomNumber = random.randint(0,count-1)
            return self.studies.find().limit(-1).skip(randomNumber).next()
        except:
            return None

    def deleteStudy(self,study_id,owner):
        try:
            self.studies.remove( { '_id' : ObjectId(study_id), 'owner': owner })
            return True
        except:
            return None

    def deleteStudyAdmin(self,study_id):
        try:
            self.studies.remove( { '_id' : ObjectId(study_id)})
            return True
        except:
            return None

    def returnObjectId(self,study_id):
        return ObjectId(study_id)

    def getStudies(self,owner):
        try:
            return self.studies.find({'owner':owner})
        except:
            return None

    def getStudiesAdmin(self):
        try:
            return self.studies.find()
        except:
            return None

    def getNewStudies(self,limit):
        try:
            return self.studies.find().limit(limit)
        except:
            return None

    def getPopularStudies(self,limit):
        try:
            return self.studies.find().limit(limit)
        except:
            return None

    def getInactiveStudies(self,limit):
        try:
            return self.studies.find().limit(limit) #Need to add votes_needed field for studies to track how long they have to go.
        except:
            return None

#--------------------Places
    def getPlaces(self,owner):
        try:
            return self.places.find({'owner':owner})
        except:
            return None

    def getPlace(self,place_id):
        try:
            return self.places.find_one(ObjectId(place_id))
        except:
            return None
            
    def deletePlace_Locations(self,place_id):
        try:
            self.places.remove( { '_id' : ObjectId(place_id) })
            self.locations.remove( { 'place_id' : str(place_id) })
            return True
        except:
            return None

    def getNewCities(self,limit):
        try:
            return self.studies.find().limit(limit)
        except:
            return None

#--------------------Locations
    def getLocations(self,place_id,limit=96):
        try:
            return self.locations.find({'place_id': place_id}).limit(limit)
        except:
            return None
    
    def getLocationsByOwner(self,owner):
        try:
            return self.locations.find({'owner': owner})
        except:
            return None
    
    def getLocation(self,location_id):
        try:
            return self.locations.find_one(ObjectId(location_id))
        except:
            return None
            
    def updateLocation(self,location_id,heading,pitch):
        try:
            self.locations.update( { '_id' : ObjectId(location_id) } , { '$set' : { 'heading' : heading, 'pitch' : pitch } } )
            return True
        except:
            return None
        
    def deleteLocation(self,location_id):
        try:
            self.locations.remove( { '_id' : ObjectId(location_id) })
            return True
        except:
            return None

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
        try:
            # FIXME: Normalize use of ObjectId/str for _id's.
            return self.votes.find({
                "$or":[
                    {'study_id': study_id},
                    {'study_id': ObjectId(study_id)}
                ]
            })
        except:
            return None

    def getVotesCount(self, study_id=None):
        try:
            if study_id is not None:
                return self.votes.find({"study_id": study_id}).count()
            else:
                return self.votes.find().count()
        except:
            return None      
                  
#--------------------QS
    def getQS(self,study_id,location_id):
        try:
            return self.qs.find({ 
                "study_id": study_id, 
                "location_id": location_id 
            }).next()
        except:
            return None

    def updateQS(self,study_id,location_id,q):
        try:
            self.qs.update( { 
                'study_id': study_id ,
                'location_id' : location_id 
            } , { '$set' : { 'q' : q } }, True )
            return True
        except:
            return None

    def incQSVoteCount(self,study_id,location_id):
        try:
            self.qs.update( { 
                'study_id': study_id ,
                'location_id' : location_id 
            } , { '$inc' : { 'num_votes': 1 } } , True)
            return True
        except:
            return None

    def randomQS(self, study_id, exclude=None, sort=None, fewestVotes=False):
        try:
            o = { 'study_id': study_id }
            if exclude is not None: o['location_id'] = { '$ne' : exclude }
            if fewestVotes: 
                f = 10
                s = randint(0,min(f,self.qs.find(o).count()-1)) 
                QS = self.qs.find(o).sort('num_votes',ASCENDING).limit(f).skip(s).next()
            else:
                s = randint(0, self.qs.find(o).count()-1)
                QS = self.qs.find(o).skip(s).limit(1).next()
            if QS.get('num_votes')  > 30 and sort is None:
                return self.randomQS(study_id, exclude=exclude, sort=True)
            return QS
        except:
            return None
    
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
    def db(self):
        if not hasattr(self, '_db'):
            dbName = os.environ['MONGO_DBNAME']
            self._db = self.conn[dbName]
            if os.environ.get('MONGO_USER') and os.environ.get('MONGO_PASSWORD'):
                self._db.authenticate(os.environ['MONGO_USER'],os.environ['MONGO_PASSWORD'])
        return self._db
    
    @property
    def conn(self):
        if not hasattr(self, '_conn'):
            self._conn = pymongo.Connection(os.environ['MONGO_HOSTNAME'], port=int(os.environ['MONGO_PORT']))
        return self._conn

Database = database()
