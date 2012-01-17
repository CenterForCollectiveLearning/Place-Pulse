import os
import pymongo
from pymongo.objectid import ObjectId

class database(object):
    def getStudy(self,study_id):
        try:
            return self.studies.find_one(ObjectId(study_id))
        except:
            return None
        
    def getPlace(self,place_id):
        try:
            return self.places.find_one(ObjectId(place_id))
        except:
            return None

    @property
    def votes(self):
        return self.db.votes
    
    @property
    def studies(self):
        return self.db.studies
        
    @property
    def places(self):
        return self.db.places
    
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