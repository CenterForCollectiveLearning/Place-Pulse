# IPython log file
import json
import igraph

nextNodeIdx = 0
def getOrMakeCity(sql_id):
    global nextNodeIdx
    if sql_id == 0: return 0
    if locs[sql_id].get('g_id'):
        return locs[sql_id].get('g_id')
    else:
        g.add_vertices(1)
        nextNodeIdx += 1
        return nextNodeIdx-1


f = open('locations_dump.json','r')
objs = map(json.loads,f.readlines())
locs = {}
for o in objs:
    for pl in o.get('places'):
        locs[pl['sql_id']]=pl
f.close()
f = open('votes_dump.json')
votes = map(json.loads,f.readlines())
f.close()
g=igraph.Graph(directed=True)
nthVote = 0
print "start adding votes to graph"
for v in votes:
    l = getOrMakeCity(v.get('left_sql_id'))
    r = getOrMakeCity(v.get('right_sql_id'))
    if l == 0 or r == 0: continue
    g.add_edges((l,r))
    nthVote += 1
    if nthVote % 100 == 0:
        print nthVote