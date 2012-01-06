import os
import pymongo
from pymongo.objectid import ObjectId

class database(object):
    def getStudy(self,study_id):
        return self.studies.find_one(ObjectId(study_id))
    
    @property
    def studies(self):
        return self.db.studies
        
    @property
    def places(self):
        return self.db.places
    
    @property
    def db(self):
        if not hasattr(self, '_db'):
            self._db = self.conn.placepulse
        return self._db
    
    @property
    def conn(self):
        if not hasattr(self, '_conn'):
            self._conn = pymongo.Connection(os.environ['MONGO_HOSTNAME'], port=int(os.environ['MONGO_PORT']))
        return self._conn

Database = database()