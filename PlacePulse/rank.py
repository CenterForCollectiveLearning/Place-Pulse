from db import Database
import numpy
from bson.objectid import ObjectId
import time

def process_studies():
    studies = Database.getStudiesAdmin()
    for study in studies:
        study_id = str(study['_id'])
        print 'processing study', study['study_question']
        placeid2scores = {}
        minscore = 1000000
        maxscore = -1
        for qscore in Database.qs.find({'study_id': study_id}):
            place_id = qscore['place_id']
            score = qscore['trueskill']['score']
            if place_id not in placeid2scores: placeid2scores[place_id] = []
            placeid2scores[place_id].append(score)
            maxscore = max(maxscore, score)
            minscore = min(minscore, score)
        
        # compute mean score and stdev for every city
        for place_id in placeid2scores:
            scores = placeid2scores[place_id]
            # first normalize scores to be between 1 and 10
            for i in xrange(len(scores)):
                scores[i] = (((scores[i]-minscore)/(maxscore - minscore)) * 9) + 1
            mean = numpy.mean(scores)
            std = numpy.std(scores)
            Database.qs_place.update({'study_id': study_id, 'place_id': place_id}, {
                '$set': { 'trueskill.mean': mean,'trueskill.std': std }})
            

sleepmin = 10
while True:
    process_studies()
    print 'sleeping', sleepmin, 'minutes'
    time.sleep(sleepmin*60)