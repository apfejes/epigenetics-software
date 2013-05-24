'''
Created on 2013-05-23

@author: sperez

'''
import Mongo_Connector
from time import time
import sys
import numpy as np

database = "human_epigenetics"
collection = "methylation"
chromosome = "chr4"
window_size = 1 #for binning purposes
start = 324567600
end = 3076407


def Findprobes(database, collection, chromosome = None, start = None, end = None):
    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database)
    mongo.ensure_index(collection, 'CHR')
    
    #First we check inputs are okay!
    t0 = time()
    Chromosomes = mongo.distinct(collection, "CHR")
    if chromosome not in Chromosomes:
        print "Invalid chromosome name. Please chose from the following:", Chromosomes.encode("utf-8")
    Starts = mongo.distinct(collection, "start_position")
    if start not in [min(Starts),max(Starts)]:
        print "Invalid starting position. Please choose between:", min(Starts),"and", max(Starts)
        
    print "Check done in", round(time()-t0,1)
    
    query = {"CHR":chromosome, "start_position":{"$lte":end},
             "end_position":{"$gte":start}}
    
    return_chr = {'_id': False, 'beta_value': True, 
                  'start_position': True, 'end_position': True, 
                  'sample_label': True}
    
    t0=time()
    probes = mongo.find(collection,query,return_chr).sort('start_position', 1)
    
    if probes.count()== 0:
        print "WARNING: The following query return zero probes!"
        print "---> Find(", query, ")"
        print "Exiting..."
        sys.exit()
        
    print "Conducting query: Find(", query, ")"
    print "Found %i probes in %f. Extracting position and beta values..." %probes.count() %(time()-t0)
    return probes
    


def BetaValues(probes):
    position_dic = {}
    betasamp_list = []
    count = 0
    for doc in probes:
        if count == 0:
            prev_start_pos = doc['start_position']
        if count != 0:
            if (doc['start_position'] - prev_start_pos) > window_size:
                avg_position = (doc['start_position'] + prev_start_pos) / 2
                position_dic[avg_position] = betasamp_list
                betasamp_list = []
                prev_start_pos = doc['start_position']
        betasamp_list.append((doc['beta_value'], doc['sample_label']))
        count += 1
    avg_position = (doc['start_position'] + prev_start_pos) / 2
    position_dic[avg_position] = betasamp_list
      
    print('%s of %s probes analyzed.' %(count, probes.count()))
      
    x_position = []
    y_avg = []
    for pos, tup_list in sorted(position_dic.iteritems()):
        beta_values = []
        for beta, samp in tup_list:
            beta_values.append(beta)
        data_avg = np.mean(beta_values)
        x_position.append(pos)
        y_avg.append(data_avg)

    return x_position, y_avg

  

probes = Findprobes(database, collection, chromosome,start,end)
x,y =BetaValues(probes)