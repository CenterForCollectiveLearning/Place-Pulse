#Phil Salesses 2/2/2012
#Michael Wong 3/22/2012
import sys
import csv, random, operator, math
from collections import defaultdict
from PlacePulse.db import Database
from PlacePulse.util import slugify

def generate_results_page(study_id,final_rankings):
    print "generate_results_page"
    studyObj = Database.getStudy(study_id)
    results = {
        "study_id": study_id,
        "question": studyObj['study_question'],
        "ranking": []
    }
    # TODO: Optimize this so that it doesn't run one query per
    # location just to fetch the place_id.
    study_places = set(map(str,studyObj['places_id']))
    places = defaultdict(list)
    for rankedLocationID in final_rankings:
        locationObj = Database.getLocation(rankedLocationID)
        # Get the place_ids shared (set intersection) between the study and this location.
        # I'm assuming there'll only be one in common, since a location should appear
        # in a study only once.
        # place_id = list(study_places&set(locationObj['place_id']))[0]
        place_id = list(study_places&set(locationObj['places_id']))[0]
        score = final_rankings[rankedLocationID]
        places[place_id].append({
            "location_id": rankedLocationID,
            "score": score,
            "loc": locationObj['loc'],
            "heading": locationObj['heading'],
            "pitch": locationObj['pitch'],
            "study_rank": len(places[place_id])+1
        })
    for place_id in places.keys():
        places[place_id].sort(key=lambda x:x['score'])
        placeObj = Database.getPlace(place_id)
        placeRanking = {
            "name": placeObj.get('name'),
            "name_slug": slugify(placeObj.get('name')),
            "place_id": place_id,
            "rankings": places[place_id]
        }
        results['ranking'].append(placeRanking)
    Database.results.update({
        "study_id": study_id,
    },
    {
        "study_id": study_id,
        "results": results
    },True)
    
def load_from_db(study_id):
    # load votes from db
    votesCursor = Database.getVotes(str(study_id))
    votes = [vote for vote in votesCursor]
    votes_selected = []
    for vote in votes:
        reformatted_vote = {}
        reformatted_vote['id_left'] = vote.get('left')
        reformatted_vote['id_right'] = vote.get('right')
        if vote.get('choice') == 'left':
            reformatted_vote['winner'] = vote.get('left')
        elif vote.get('choice') == 'right':
            reformatted_vote['winner'] = vote.get('right')
        elif vote.get('choice') == 'equal':
            reformatted_vote['winner'] = '0'
        votes_selected.append(reformatted_vote)
    return votes_selected

def calculate_win_loss(images, votes_selected):    
    temp_scores = defaultdict(lambda: defaultdict(float))
    for j in range(1,101):
        #Variables
        play = defaultdict(float) #Number of times an image is voted on
        neighbors = defaultdict(set) #Number of neighbors each ID has in graph
        WL = defaultdict(lambda: defaultdict(float)) #Win/Loss
        LW = defaultdict(lambda: defaultdict(float)) #Loss/Win
        W = defaultdict(float) #Wins
        T = defaultdict(float) #Ties
        WR = defaultdict(float) #Win Ratio
        LR = defaultdict(float) #Loss Ratio
        WR1 = defaultdict(float) #Win Ratio + Indirect Wins of Neighbor
        WR_int = {}
        alpha = 1 #Tuning Parameter
        counter = 0    
        
        #Cycle through votes and set hashes
        for vote in votes_selected:
            #Is it one of the the selected images?
			counter += 1
			play[vote['id_left']] += 1
			play[vote['id_right']] += 1
			neighbors[vote['id_left']].add(vote['id_right'])
			neighbors[vote['id_right']].add(vote['id_left'])
			if vote['winner'] == vote['id_left']:
				WL[vote['id_left']][vote['id_right']] += 3
				LW[vote['id_right']][vote['id_left']] += 3
				W[vote['id_left']] += 1
			elif vote['winner'] == vote['id_right']:
				WL[vote['id_right']][vote['id_left']] += 3
				LW[vote['id_left']][vote['id_right']] += 3
				W[vote['id_right']] += 1
			elif vote['winner'] == '0':
				WL[vote['id_right']][vote['id_left']] += 1
				LW[vote['id_left']][vote['id_right']] += 1
				T[vote['id_left']] += 1
				T[vote['id_right']] += 1
        #Calculate First order        
        for key, value in play.iteritems():
            WR[key] = W[key] / play[key]
            LR[key] = (play[key] - W[key] - T[key]) / play[key]
        #Calculate Second order
        for key, value in play.iteritems():
            WR1[key] = WR[key]
            for key1, value1 in WL[key].iteritems():
                WR1[key] += alpha * WR[key1] / len(neighbors[key1])
            for key1, value1 in LW[key].iteritems():
                WR1[key] -= alpha * LR[key1] / len(neighbors[key1])
        #Write to temp_scores
        for key, value in play.iteritems():
            temp_scores[key]['WR1'] += value
            temp_scores[key]['votes'] += 1   
    final_rankings = defaultdict(lambda: defaultdict(float))
    for key, value in temp_scores.iteritems():
        #Need to calculate STD Deviation
        WR1 = temp_scores[key]['WR1'] / temp_scores[key]['votes']                
        final_rankings[key] = WR1      
    minVal = 0
    maxVal = 0
    for key, value in final_rankings.iteritems():
        wr1 = value
        if wr1 > maxVal:
            maxVal = wr1
        elif wr1 < minVal:
            minVal = wr1
    for key, value in final_rankings.iteritems():
        wr1 = (value - minVal)/(maxVal - minVal)
        final_rankings[key] = wr1
    return final_rankings

def set_image_hash(votes_selected):
    images = {}
    for vote in votes_selected:
        images[vote['id_left']] = images.get(vote['id_left'], 0) + 1
        images[vote['id_right']] = images.get(vote['id_right'], 0) + 1
    return images

def rank_mongo(study_id=None):
    if study_id:
        study = Database.getStudy(study_id)
    else:
        study = Database.getRandomStudy()
    study_id = study.get('_id')
    print "processing study: %s" % study_id

    votes_selected = load_from_db(study_id)
    
    if len(votes_selected) == 0:
        print "no votes eligible, exiting"
        return
    
    output_file = "data/db.csv"
    print str(len(votes_selected)) + " eligible votes"

    #Set Image Hash
    images = set_image_hash(votes_selected)
    print str(len(images)) + " images in total"
    
    #Rank all images
    final_rankings = calculate_win_loss(images, votes_selected)
    # print ""
    # print "*** FINAL RANKINGS ***"
    # print final_rankings
    
    #Load Results to db
    print len(final_rankings)
    for location_id, q in final_rankings.iteritems():
        if Database.updateQS(str(study_id),location_id,q) is None:
             print "Could not update score for %s" % location_id
             
    # Generate results page data
    generate_results_page(study_id, final_rankings)
    return 1

if __name__ == '__main__':
    rankStudy = None
    if len(sys.argv) == 2:
        rankStudy = sys.argv[1]
    sys.exit(rank_mongo(study_id=rankStudy))