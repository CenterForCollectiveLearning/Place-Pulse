from PlacePulse import app

import json

class Buckets:
    Unknown, Queue, Archive = range(3)
    QueueSize = 100

def jsonifyResponse(obj):
    resp = app.make_response(json.dumps(obj))
    resp.mimetype = 'application/json'
    return resp

def objifyPlace(place):
    return {
        'id' : str(place['_id']),
        'loc' : place['loc']
    }
