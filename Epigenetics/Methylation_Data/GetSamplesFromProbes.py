'''
Created on 2013-04-18

@author: jyeung

Motivation: from a list of probes, can we plot the different samples? 
'''


import sys
import os
import time
import csv
import pymongo
import matplotlib.pyplot as plt

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)

from MongoDB.mongoUtilities import Mongo_Connector
from annotUtilities import plots


database_name = 'human_epigenetics'
annotation_collection = 'annotations'
methylation_collection = 'methylation'
samples_collection = 'samples'
prefix = 'humanmethylation450_beadchip_'    # prefix + TargetID = probe id
suspected_samples = ['DS09A M', 'DS01A M', 'DS04A F', 'DS06A M', 'DS10A M']
# Suspected samples are used for coloring purposes. These may be blood contaminated. 

def GetProbesFromHits(probe_list_fname, skip_rows):
    '''
    Get list of probes from probe_list_fname, also get other values such as 
    expected difference in beta values. 
    
    Returns two values: a list of probes and a list of 'expected beta difference'
    between blood and buccal. This can be helpful for plotting because 
    if the directionality of the difference between blood and buccal could
    be informative/predictive. 
    '''
    probe_list = []
    delta_beta = []
    cg_no = []
    take_top_n_hits = 50    # Take top n hits. 
    count = 0
    # Grab information regarding buccal vs. blood. 
    with open(probe_list_fname, 'rb') as hit_file:
        probe_reader = csv.reader(hit_file, delimiter='\t')
        for i in xrange(skip_rows):
            probe_reader.next()
        for row in probe_reader:
            probe_list.append(row[0])    # Probe_iD
            delta_beta.append(row[5])    # Expected beta diff btwn buccal vs blood
            cg_no.append(row[23])    # cg_no (x-axis of the plot)
            count += 1
            if count > take_top_n_hits:
                break
    
    cg_delta_beta_list = []
    for i in xrange(len(delta_beta)):
        if float(delta_beta[i]) >= 0:
            above_or_below = 'greater'    # Expect beta in blood greater than beta in buccal
        elif float(delta_beta[i]) < 0:
            above_or_below = 'lesser'    # Expect beta in blood less than beta in buccal
        cg_delta_beta_tuple = (cg_no[i], above_or_below)
        cg_delta_beta_list.append(cg_delta_beta_tuple)
    
    return {'probe_list': probe_list, 'tuple_list': cg_delta_beta_list}
    
def GetDataFromProbeList(probe_list):
    '''
    From a list of probes, get data from samples. 
    '''
    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)
    
    # Find dummy probes from annotation collection.
    fAnnotQuery = {'Probe_ID': {'$in': probe_list}}    # Find all docs in annotations collection
    rAnnotQuery = {'cg_no': True, 'Chromosome': True}
    print('Finding annotation information...')
    annot_cursor = mongo.find(annotation_collection, findQuery=fAnnotQuery, 
                              returnQuery=rAnnotQuery)
    probe_list_dic = list(annot_cursor)
    print('Probe list length: %s' % len(probe_list_dic))
    
    # Attach prefix to probename for searching in methylation collection
    probe_list = []
    for probe_dic in probe_list_dic:
        probe_list.append(''. join((prefix, probe_dic['cg_no'])))
    print probe_list
    
    '''
    From probe_list, get sample data. Then find number of samples.
    '''
    mongo.ensure_index(methylation_collection, 'annotation_id')    # For speed
    
    fQuery = {'$and': [{'annotation_id': {'$in': probe_list}}, {'project': 'down'}]}
    rQuery = {'sample_label': True, 'start_position': True, 'beta_value': True,
              'beta_value': True, 'CHR': True, '_id': False, 'annotation_id': True} 
    data_cursor = mongo.find(methylation_collection, findQuery=fQuery,
                             returnQuery=rQuery).sort([('annotation_id', pymongo.ASCENDING), 
                                                        ('sample_label', pymongo.ASCENDING)])
    print'%s data docs match probe_list' % data_cursor.count()
    
    fSampQuery = {'project': 'down'}    # 17 samples in down (unittest?)
    rSampQuery = {'patient.Total_BriefPraxis': True, 'Sample Group': True,
                  'SampleLabel': True, '_id': False}
    samples_cursor = mongo.find(samples_collection, findQuery=fSampQuery,
                                returnQuery=rSampQuery)
    samples_list = list(samples_cursor)
    
    
    '''
    Purpose of this for loop:
        Create a dictionary where keys are probe ids, values is list of M-values.
        We also want to create a list of sample_ids that should match the M-values.
        
    How I did it:
        First, define current probe of doc.
        Second, extend a list of M-values, but don't insert it into dictionary
        until we have found all the M-values in that probe.
        Third, check if current probe equals previous probe (from prev doc).
            Note: this if only applies after the first iteration (count != 0)
            If current probe != previous probe, we have found all M-vals for
            that probe. So we will create a key:value pair where key is probe_id
            and value is list of M-values. 
        Fourth, make a sample_list so we can correspond M-vals to sample. But we
        only want to make this list once, so after we have iterated through all the
        samples in the first probe, stop doing this. 
    '''
    exprs_list = []
    sample_list = []
    dataDict = {}
    prev_probe = None
    data_count = 0    # 17 samples per probe
    probe_count = 0
    for doc in data_cursor:
        current_probe = doc['annotation_id']
        if prev_probe != current_probe and data_count != 0:
            if len(exprs_list) != len(samples_list):
                print('Warning, samples per probe do not match sample number')
                print len(exprs_list)
            dataDict[prev_probe] = exprs_list
            exprs_list = []
            probe_count += 1
        if probe_count == 0:
            sample_list.append(doc['sample_label'])
        exprs_list.append(doc['beta_value'])
        prev_probe = doc['annotation_id']
        data_count += 1
    dataDict[prev_probe] = exprs_list
    
    '''
    Three if conditions for sanity check. Maybe make this into unit test?
    '''
    if len(dataDict.keys()) != len(probe_list):
        print('Warning, probe lengths do not match number of keys in dictionary')
        print('Probe length: %s' % len(probe_list))
        print('Number of keys in dict: %s' % len(dataDict.keys()))
       
    vals_per_key = [len(vals) for vals in dataDict.values()]
    if len(samples_list) not in vals_per_key:
        print('Warning, number of values in each key do not equal to number of samples')
        print('Number of samples: %s' % len(samples_list))
        print('Number of vals in each key: %s' % vals_per_key)
    
    if len(set(vals_per_key)) != 1:
        print('Warning, in consistent number of values in keys')
        print set([len(vals) for vals in dataDict.values()])
        
    return {'data_dictionary': dataDict, 'sample_list': sample_list}
        

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Filename of probelists must be given in command line.')
        sys.exit()
    probe_list_fname = sys.argv[1]
    
    # Ask how many rows to skip, more rows you skip, the lower you go on table, meaning you're
    # selecting for less significantly differentially methylated probes. 
    top_or_bot = raw_input('Take top significant differentially methylated probes or bottom? (top/bottom): ')
    if top_or_bot == 'top':
        skip_rows = 1
    elif top_or_bot == 'bottom':
        skip_rows = 800
    else:
        sys.exit('Only allowed most or least as inputs, exiting...')
    
    starttime = time.time()
    
    # Get dictionary containing probe_list and beta_difference between blood and buccal
    probe_list_and_beta_diff_dic = GetProbesFromHits(probe_list_fname, skip_rows)
    
    # Get dictionary containing a data dictionary and a sample list
    data_and_sample_dic = GetDataFromProbeList(probe_list_and_beta_diff_dic['probe_list'])
    
    # Now let's plot our data.
    data_dict = data_and_sample_dic['data_dictionary']
    sample_list = data_and_sample_dic['sample_list']
    cg_delta_beta_list = probe_list_and_beta_diff_dic['tuple_list']    # for labelling purposes
    title = 'Suspected contaminated buccal samples: for %s probes \n\
             expected to differ between buccal and blood.' % top_or_bot

    # Set plotcolors. Color suspected samples 'red'
    plotcolors = []
    for s in sample_list:
        if s in suspected_samples:
            plotcolors.append('red')
        else:
            plotcolors.append('blue')

    x_list = []    # For plotting
    for i in xrange(len(sample_list)):
        y_list = []    # Reset for every i
        for probe, val_list in data_dict.iteritems():
            if i == 0:
                x_list.append(probe.replace(prefix, ""))
            y_list.append(val_list[i])
            
        dat_plot = plots.makeXYPlot(range(len(x_list)), y_list, 'probe ID', 'Beta-value', title, 
                             sample_list[i], plotcolors[i])
    
    # Adjust x-axis, concatonate an expected delta beta value to x-axis to 
    # see expected difference between blood and buccal
    for tup in cg_delta_beta_list:
        if tup[0] in x_list:
            index_x = x_list.index(tup[0])
            x_list[index_x] = '_'.join((x_list[index_x], tup[1]))
    print x_list
    plt.xticks(range(len(x_list)), x_list, size='small', rotation=90)
    
    print('Time elapsed: %s seconds' % int(time.time()-starttime))
    
    plt.show()
        