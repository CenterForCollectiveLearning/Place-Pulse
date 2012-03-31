#Phil Salesses 2/2/2012
#Michael Wong 3/22/2012

import csv, random, operator, math, numpy
from collections import defaultdict

def pearson_corr(x, y):
    assert len(x) == len(y)
    n = len(x)
    assert n > 0
    avg_x = numpy.average(x)
    avg_y = numpy.average(y)
    diffprod = 0
    xdiff2 = 0
    ydiff2 = 0
    for idx in range(n):
        xdiff = x[idx] - avg_x
        ydiff = y[idx] - avg_y
        diffprod += xdiff * ydiff
        xdiff2 += xdiff * xdiff
        ydiff2 += ydiff * ydiff
    return diffprod / math.sqrt(xdiff2 * ydiff2)
    
def split_list(a_list):
    half = len(a_list)/2
    return a_list[:half], a_list[half:]

def load_places_from_csv(filename):
    #Load Places (id, lat, lon, id_city)
    id_locations = {}
    places = csv.DictReader(open(filename, 'rb'), delimiter=',', quotechar='"')
    for place in places:
        id_locations[int(place['id'])] = (float(place['lat']),float(place['lng']),str(place['id_city']),int(place['id_location']))
    return id_locations

def select_votes_from_csv(question, filename):
    votes_selected = []
    votes = csv.DictReader(open(filename, 'rb'), delimiter=',', quotechar='"')
    for vote in votes:
        if vote['id_question'] == question:
            votes_selected.append(vote)
    return votes_selected

def set_image_hash(votes_selected):
    images = {}
    for vote in votes_selected:
        images[int(vote['id_left'])] = 1
        images[int(vote['id_right'])] = 1
    return images
    
def calculate_rank(id_locations, images, votes_selected):    
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
    
        #Select half the data randomly
        selected_images_temp = random.sample(images, int(len(images) * 50/100))
        selected_images = {}
        for selected in selected_images_temp:
            selected_images[selected] = 1
    
        #Cycle through votes and set hashes
        for vote in votes_selected:
            #Is it one of the the selected images?
            if selected_images.get(int(vote['id_left'])) is not None:
                if selected_images.get(int(vote['id_right'])) is not None:
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
        for key, value in WL.iteritems():
            WR[key] = W[key] / play[key]
            LR[key] = (play[key] - W[key] - T[key]) / play[key]
        #Calculate Second order
        for key, value in WL.iteritems():
            WR1[key] = WR[key]
            for key1, value1 in WL[key].iteritems():
                WR1[key] += alpha * WR[key1] / len(neighbors[key1])
            for key1, value1 in LW[key].iteritems():
                WR1[key] -= alpha * LR[key1] / len(neighbors[key1])
        #Write to temp_scores
        for key, value in WR1.iteritems():
            temp_scores[int(key)]['WR1'] = temp_scores[int(key)]['WR1'] + value
            temp_scores[int(key)]['votes'] += 1   
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

def output_ranking_file(final_rankings_sorted, id_locations, FILENAME):
    rankings = csv.writer(open(FILENAME, 'wb'), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)        
    temp = "id","wr1","id_city","lat","lng","id_location"
    rankings.writerow(temp)
    for id_place, wr1 in final_rankings_sorted.iteritems():
        temp = id_place,wr1,id_locations[id_place][2],id_locations[id_place][0],id_locations[id_place][1],id_locations[id_place][3]
        rankings.writerow(temp)

# TODO: needs to be refactored before going to production
def calculate_corr(id_locations, images, votes_selected):    	
    chart_values = defaultdict(lambda: defaultdict(float))    
    for i in range (1,40):
        corr_values = []
        for j in range(1,101):
            #Shuffle Votes
            random.shuffle(votes_selected)
            #Select 10% of votes
            votes_sample = random.sample(votes_selected,int(len(votes_selected) * i/100))
            votes_half1,votes_half2  = split_list(votes_sample)
    
            final_rankings_half1 = calculate_rank(id_locations, images, votes_half1)
            final_rankings_half2 = calculate_rank(id_locations, images, votes_half2)
            
            final_rankings_half1_array = []
            final_rankings_half2_array = []
            for key, value in final_rankings_half1.iteritems():
                if key in final_rankings_half2 and not (final_rankings_half2[key] is None):
                	final_rankings_half1_array.append(float(final_rankings_half1[key]))
                	final_rankings_half2_array.append(float(final_rankings_half2[key])) 
            corr_values.append(pearson_corr(final_rankings_half1_array,final_rankings_half2_array))
        chart_values[i]['corr'] = numpy.average(corr_values)
        chart_values[i]['stddev'] = numpy.std(corr_values)
        print str(i),str(chart_values[i]['corr']),str(chart_values[i]['stddev'])
        output_corr_file(chart_values, FILENAME)
    return chart_values

def output_corr_file(chart_values, FILENAME):
    rankings = csv.writer(open(FILENAME, 'wb'), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)        
    temp = "percent","correlation","stddev"
    rankings.writerow(temp)
    for key, value in chart_values.iteritems():
        temp = key,chart_values[key]['corr'],chart_values[key]['stddev']
        rankings.writerow(temp)

def main(argv=None):
    QUESTION = "safer"
    FILENAME = "data/" + str(QUESTION) + "1.csv"
  
    #Load Places
    id_locations = load_places_from_csv("data/places2.csv")
    
    #Generate list of approved votes based on input criteria
    votes_selected = select_votes_from_csv(QUESTION, "data/votes.csv")
    print str(len(votes_selected)) + " eligible votes"

    #Set Image Hash
    images = set_image_hash(votes_selected)
    print str(len(images)) + " images in total"
    
    #Rank all images
    final_rankings = calculate_rank(id_locations, images, votes_selected)
    
    #Output Results to File
    output_ranking_file(final_rankings, id_locations, FILENAME)


if __name__ == "__main__":
    main()
