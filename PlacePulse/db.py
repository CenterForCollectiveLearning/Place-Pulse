import os
import pymongo
import random
from pymongo.objectid import ObjectId
from pymongo import ASCENDING

from random import choice
from random import randint


class database(object):
#--------------------Results
    def getResultsForStudy(self,studyName):
        try:
            return self.results.find_one({
                'question_shortid': studyName
            })
        except:
            return None

#--------------------Studies
    def getStudy(self,study_id):
        try:
            return self.studies.find_one(ObjectId(study_id))
        except:
            return None
            
    def getRandomStudy(self):
        try:
            count = self.studies.count()
            randomNumber = random.randint(0,count-1)
            return self.studies.find().limit(-1).skip(randomNumber).next()
        except:
            return None

    def returnObjectId(self,study_id):
        return ObjectId(study_id)

    def getStudies(self):
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

#--------------------Votes
    def getVotes(self,study_id):
        try:
            return self.votes.find({'study_id': study_id})
        except:
            return None

    def getVotesCount(self):
        try:
            return self.votes.find().count()
        except:
            return None
#--------------------Places
    def getPlace(self,place_id):
        try:
            return self.places.find_one(ObjectId(place_id))
        except:
            return None

    def getNewCities(self,limit):
        try:
            return self.studies.find().limit(limit)
        except:
            return None

#--------------------Locations
    def getLocations(self,place_id,limit=24):
        try:
            return self.locations.find({'place_id': place_id}).limit(limit)
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

    def randomQS(self, study_id, exclude=None, fewestVotes=False):
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
            if QS.get('num_votes')  > 30 and not sort:
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
    def votes(self):
        return self.db.votes

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
