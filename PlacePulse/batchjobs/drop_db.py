__author__ = 'Daniel Smilkov (dsmilkov@gmail.com)'

import pymongo
conn = pymongo.Connection()
conn.drop_database('placepulse')