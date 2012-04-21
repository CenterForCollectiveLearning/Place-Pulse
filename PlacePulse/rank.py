#Phil Salesses 2/2/2012
#Michael Wong 3/22/2012
import sys
import csv, random, operator, math, numpy
from scipy.stats import norm
from scipy.optimize import fmin_powell
from scipy.optimize import fmin_ncg
from collections import defaultdict
from db import Database

# TODO: load_from_db should specify study instead of random, e.g.
#     if Database.getStudy(study_id) is None:
#         return jsonifyResponse({
#             'error': 'Study doesn\'t exist!'
#         })

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
    
def load_places_from_csv(filename):
    #Load Places (id, lat, lon, id_city)
    id_locations = {}
    places = csv.DictReader(open(filename, 'rb'), delimiter=',', quotechar='"')
    for place in places:
        id_locations[place['id']] = (float(place['lat']),float(place['lng']),str(place['id_city']),int(place['id_location']))
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
        images[vote['id_left']] = images.get(vote['id_left'], 0) + 1
        images[vote['id_right']] = images.get(vote['id_right'], 0) + 1
    return images
    
def calculate_max_likelihood(images, votes_selected):
    # prepare lookup tables
    image_ids = images.keys()
    image_index_lookup = dict([(image_ids[i], i) for i in range(len(image_ids))])
    
    # make vote matrix
    m = [[0.2]*len(image_ids)]*len(image_ids)
    m = numpy.matrix(m)
    for i in range(len(image_ids)):
        m[i,i] =  0.
    for vote in votes_selected:
        index_left = image_index_lookup.get(vote['id_left'])
        index_right = image_index_lookup.get(vote['id_right'])
        print vote
        if vote['winner'] == vote['id_left']:
            m[index_left, index_right] += 1.
        elif vote['winner'] == vote['id_right']:
            m[index_right, index_left] += 1.
        elif vote['winner'] == '0':
            m[index_left, index_right] += 0.5
            m[index_right, index_left] += 0.5
    
    #test
    #m = test_matrix1()

    # log likelihood function
    def neg_log_likelihood(s, m):
        s = numpy.append(s, 0.)
        sum = 0.
        for i in range(s.shape[0]):
            for j in range(s.shape[0]):
                x = s[i] - s[j]
                y = 1.5976 * x * (1 + 0.04417 * x * x)
                try: z = y - math.log(1 + math.exp(y))
                except OverflowError: z = 0.
                sum -= m[i,j] * z
        return sum
    
    # normal dist cdf approximation
    def norm_cdf(x):
        y = 1.5976 * x * (1 + 0.04417 * x * x)
        try:
            return math.exp(y)/(1 + math.exp(y))
        except OverflowError:
            return 1.
        
    def gradient(s, m):
        g = numpy.zeros(shape=(s.shape[0]))
        for i in range(g.shape[0]):
            sum = 0
            for j in range(g.shape[0]):
                r1 = norm.pdf(s[i]- s[j])/norm_cdf(s[i]- s[j])
                if math.isinf(r1): r1 = 0.
                r2 = norm.pdf(s[j]- s[i])/norm_cdf(s[j]- s[i])
                if math.isinf(r2): r2 = 0.
                sum += m[i,j] * r1
                sum -= m[j,i] * r2
            g[i] = sum
        return g
    
    def hessian(s, m):
        s = numpy.append(s, 0.)
        h = numpy.zeros(shape=(s.shape[0], s.shape[0]))
        h = numpy.matrix(h)
        for i in range(h.shape[0]):
            for k in range(i+1, h.shape[1]):
                r1 = norm.pdf(s[i]- s[k])/norm_cdf(s[i]- s[k])
                if math.isinf(r1): r1 = 0.
                r2 = norm.pdf(s[k]- s[i])/norm_cdf(s[k]- s[i])
                if math.isinf(r2): r2 = 0.
                temp = m[i,k] * r1 * (s[i] - s[k] + r1) + m[k,i] * r2 * (s[k] - s[i] + r2)
                h[i,k] = temp
                h[k,i] = temp
                h[i,i] -= temp
                h[k,k] -= temp
        return h[:-1,:-1]
    
    # find strength parameters that minimize log likelihood function
    s0 = numpy.zeros(m.shape[0]-1)
    #s = fmin_powell(neg_log_likelihood, s0, args=(m,), disp=True)
    s = fmin_ncg(neg_log_likelihood, s0, gradient, fhess=hessian, args=(m,))

    h = hessian(s, m)
    covar = numpy.linalg.inv(-h)
    print "covariance matrix:" 
    print covar
    
    # return strength rankings
    rankings = defaultdict(lambda: defaultdict(int))
    s = numpy.append(s, 0.)
    for i in range(s.shape[0]):
        rankings[image_ids[i]] = s[i]
    return rankings
   
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
    
        #Select half the data randomly
        selected_images_temp = random.sample(images, int(len(images) * 50/100))
        selected_images = {}
        for selected in selected_images_temp:
            selected_images[selected] = 1
    
        #Cycle through votes and set hashes
        for vote in votes_selected:
            #Is it one of the the selected images?
            if selected_images.get(vote['id_left']) is not None:
                if selected_images.get(vote['id_right']) is not None:
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
            temp_scores[key]['WR1'] = temp_scores[key]['WR1'] + value
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

def output_ranking_file(final_rankings, FILENAME, id_locations=None):
    rankings = csv.writer(open(FILENAME, 'wb'), delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)       
    if id_locations != None:
        temp = "id","wr1","id_city","lat","lng","id_location"
        rankings.writerow(temp)
        for id_place, wr1 in final_rankings.iteritems():
            temp = id_place,wr1,id_locations[id_place][2],id_locations[id_place][0],id_locations[id_place][1],id_locations[id_place][3]
            rankings.writerow(temp)
    else:
        temp = "id","score"
        for id_place, score in final_rankings.iteritems():
            temp = id_place, score
            rankings.writerow(temp)

def calculate_corr(images, votes_selected):
    
    def split_list(a_list):
        half = len(a_list)/2
        return a_list[:half], a_list[half:]
        
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
        
    chart_values = defaultdict(lambda: defaultdict(float))
    for i in range (1,40):
        corr_values = []
        for j in range(1,101):
            random.shuffle(votes_selected)
            #Select 10% of votes
            votes_sample = random.sample(votes_selected,int(len(votes_selected) * i/100))
            votes_half1,votes_half2  = split_list(votes_sample)
    
            final_rankings_half1 = calculate_rank(images, votes_half1)
            final_rankings_half2 = calculate_rank(images, votes_half2)
            
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

def rank_csv():    
    question = "safer"
    output_file = "data/"+question+".csv"
    places_csv = "data/places2.csv"
    votes_csv = "data/votes200.csv"

    #Load Places
    id_locations = load_places_from_csv(places_csv)
    
    #Generate list of approved votes based on input criteria
    votes_selected = select_votes_from_csv(question, votes_csv)
    print str(len(votes_selected)) + " eligible votes"

    #Set Image Hash
    images = set_image_hash(votes_selected)
    print str(len(images)) + " images in total"
    
    #Rank all images
    final_rankings = calculate_max_likelihood(images, votes_selected)
    
    #Output Results to File
    output_ranking_file(final_rankings, output_file, id_locations)

def rank_mongo():
    study = Database.getRandomStudy()
    study_id = study.get('_id')
    print "processing study: %s" % study_id

    votes_selected = load_from_db(study_id)
    
    if votes_selected == 0:
        print "no votes eligible, exiting"
        return
    
    output_file = "data/db.csv"
    print str(len(votes_selected)) + " eligible votes"

    #Set Image Hash
    images = set_image_hash(votes_selected)
    print str(len(images)) + " images in total"
    
    #Rank all images
    final_rankings = calculate_win_loss(images, votes_selected)
    
    #Load Results to db
    print "\n\n\n"
    print "FINAL RANKINGS"
    print final_rankings
    for location_id, q in final_rankings.iteritems():
        if not Database.updateLocationScore(study_id,location_id,q,images[location_id]):
             print "Could not update score for %s" % location_id
    return

def test_matrix1():
    m = numpy.matrix([[0,.1,.1,.1,.1],[.1,0,.1,.1,.1],[.1,.1,0,.1,.1],[.1,.1,.1,0,.1],[.1,.1,.1,.1,0]])
    m[0,1] += 5
    m[1,0] += 4
    m[0,2] += 3
    m[0,3] += 5
    m[0,4] += 6
    m[1,2] += 4
    m[1,3] += 6
    m[1,4] += 3
    m[2,3] += 5
    m[2,4] += 4
    m[3,4] += 2
    return m

def test_matrix2():
    m = numpy.matrix([[0,.1,.1,.1,.1],[.1,0,.1,.1,.1],[.1,.1,0,.1,.1],[.1,.1,.1,0,.1],[.1,.1,.1,.1,0]])
    m[0,1] += 50
    m[1,0] += 40
    m[0,2] += 30
    m[0,3] += 50
    m[0,4] += 60
    m[1,2] += 40
    m[1,3] += 60
    m[1,4] += 30
    m[2,3] += 50
    m[2,4] += 40
    m[3,4] += 20
    return m

def test_basic():
    m = numpy.matrix([[0,.1],[.1,0]])
    m[0,1] += 1
    m[1,0] += 1
    return m

if __name__ == '__main__':
    sys.exit(rank_mongo())
