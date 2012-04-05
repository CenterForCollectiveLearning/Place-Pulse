from random import shuffle

from PlacePulse.db import database
from PlacePulse.util import slugify

Database = database()

# Run this to populate the results collection with some fake data.

studies = [
    {
        'city_name': u"Sao Paulo",
        'study_id': '4f7ce4f87edf1f7ecf000000'
    },
    {
        'city_name': 'Boston',
        'study_id': '4f7ce54f7edf1f7ecf000065'
    },
    {
        'city_name': 'NYC',
        'study_id': '4f7ce59e7edf1f7ecf0000ca'
    },
    {
        'city_name': 'Tokyo',
        'study_id': '4f7ce61a7edf1f7ecf000130'
    },
    {
        'city_name': 'Mexico City',
        'study_id': '4f7ce6737edf1f7ecf000196'
    }
]

for city in studies:
    city['city_name_id'] = slugify(city['city_name'])

def genTestResults(studies,question="Which place looks more unique?",question_shortid='unique'):
    # Get 70 locations for each city
    testResults = {
        'question': question,
        'question_shortid': question_shortid,
        'study_type': 'main_study',
        'ranking': []
    }
    site_rank = 1
    shuffle(studies)
    for city in studies:
        locs = Database.getLocations(city['study_id'],70)
        locs = [i for i in locs]
        shuffle(locs)
        city['places'] = []
        for i in range(len(locs)):
            loc = {
                "coords": locs[i]['loc'],
                "type": "streetview"
            }
            loc['site_rank'] = site_rank
            loc['city_rank'] = i
            city['places'].append(loc)
            site_rank += 1
        testResults['ranking'].append(city)
        
    Database.results.insert(testResults)

genTestResults(studies)
genTestResults(studies,"Which place looks safer?","safer")
genTestResults(studies,"Which place looks more upper class?","upper_class")
genTestResults(studies,"Which place looks more lively?","lively")
genTestResults(studies,"Which place looks more modern?","modern")
genTestResults(studies,"Which place looks more central?","central")
genTestResults(studies,"Which place looks more groomed?","groomed")