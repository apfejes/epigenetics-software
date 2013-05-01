'''
Created on 2013-04-16

@author: jyeung
'''


import sys
import os
import matplotlib.pyplot as plt
import time

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
from annotUtilities import plots

starttime = time.time()
# database_name = 'human_epigenetics'
database_name = 'jake_test'
annotation_collection = 'annotations'
methylation_collection = 'methylation'
sample_collection = 'samples'
# project = 'kollman'
# feature = 'stimulation'
# control_group_label = 'unstimulated'
# diseased_group_label = 'listeria'
project = 'down'
feature = 'Sample Group'
control_group_label = 'Control'
diseased_group_label = 'DS'
window_size = 1   # For binning purposes
savedirectory = '/home/jyeung/Documents/Presentations/batchplots/'

'''
control_samples = ['09 Adult 3 unstim', '15 Cord 2 unstim', '13 Old 3 Unstim', 
                   '17 Cord 3 Unstim', '11 Old 2 Unstim', '07 Adult 2 Unstim']
diseased_samples = ['10 Adult 3 Lm', '08 Adult 2 Lm', '14 Old 3 Lm', 
                    '12 Old 2 Lm', '16 Cord 2 Lm', '18 Cord 3 Lm']
'''
'''
project = 'down'
control_samples = ['C4ab1 M', 'C4ab2 M', 'C5a M', 'C3a F', 'C1ab F', 'C2a M', 'C2c M']
diseased_samples = ['DS01A M', 'DS09A M', 'DS02A F', 'DS04A F', 'DS03A F', 
                    'DS05A F', 'DS08B F', 'DS06A M', 'DS07A M', 'DS10A M']
'''

def CreateSampleGroups(mongo, project, feature):
    '''
    Separate samples into 'groups' according to a particular feature.
    Example: feature = diseased/control, sex, tissue type...
    
    Returns a dictionary of key:value pairs where key is the name of the 
    feature (e.g. diseased/control) and value is a list of sample labels
    that are in that feature group. 
    '''
    mongo.ensure_index(sample_collection, project)    # For speed
    mongo.ensure_index(sample_collection, feature)
    
    findQuery = {'project': project}
    returnQuery = {feature: True, '_id': False, 'sample_label': True}
    
    
    samples = mongo.find(sample_collection, 
                        findQuery, returnQuery).sort(feature, 1)
    sample_groups = {}
    sample_labels_list = []
    previous_group = None
    count = 0
    for doc in samples:
        '''
        For each doc, keep track of previous group feature (e.g. whether
        previous doc was diseased or control). Since it is ordered by 
        the feature, it will go through all of samples of one feature 
        before moving on to the other. We use this as an indicator that
        all samples in that group have been iterated.
        
        We keep extending a list, sample_label_list, to add sample_labels
        for all the samples within one group. 
        
        When all samples in that group have been iterated (the if statement),
        then we create a key:value pair in the dictionary, sample_groups, where
        key is the feature (e.g. diseased or control) and value is sample_label_list.
        
        Empty sample_label_list and keep doing this for all feature groups. 
        '''
        if (doc[feature] != previous_group) and (count > 0):
            sample_groups[previous_group] = sample_labels_list
            sample_labels_list = []
        sample_labels_list.append(doc['sample_label'])
        previous_group = doc[feature]
        count += 1
    sample_groups[previous_group] = sample_labels_list  # Do once more after exiting loop
    return sample_groups

               
def PlotBetaDiff(mongo, project, chromosome, control_samples, diseased_samples, window_size):
    '''
    We plot differences in betas between controls and diseased. Only works for two groups. 
    '''
    
    mongo.ensure_index(methylation_collection, 'CHR')
    mongo.ensure_index(methylation_collection, 'annotation_id')
    mongo.ensure_index(methylation_collection, 'sample_label')
    mongo.ensure_index(methylation_collection, 'start_position')
    
    query_project = {'project': project}
    query_chr = {'CHR': chromosome}
    andQuery = {'$and': [query_chr, query_project]}
    
    return_chr = {'_id': False, 'beta_value': True, 
                  'start_position': True, 'end_position': True, 
                  'sample_label': True}
    probes_chr = mongo.find(methylation_collection, 
                            andQuery, return_chr).sort('start_position', 1)
                                                        
    position_dic = {}
    betasamp_list = []
    # prev_start_pos = None
    count = 0
    for doc in probes_chr:
        if count == 0:
            prev_start_pos = doc['start_position']
        if count != 0:
            # if doc['start_position'] != prev_start_pos:
            if (doc['start_position'] - prev_start_pos) > window_size:
                avg_position = (doc['start_position'] + prev_start_pos) / 2
                # print doc['start_position'], prev_start_pos, avg_position
                position_dic[avg_position] = betasamp_list
                # position_dic[prev_start_pos] = betasamp_list
                betasamp_list = []
                prev_start_pos = doc['start_position']
        betasamp_list.append((doc['beta_value'], doc['sample_label']))
        count += 1
        # prev_start_pos = doc['start_position']
    # position_dic[prev_start_pos] = betasamp_list
    avg_position = (doc['start_position'] + prev_start_pos) / 2
    position_dic[avg_position] = betasamp_list
    
    x_position = []
    y_diffavg = []
    for pos, tup_list in sorted(position_dic.iteritems()):
        controls = []
        diseased = []
        for beta, samp in tup_list:
            if samp in control_samples:
                controls.append(beta)
            elif samp in diseased_samples:
                diseased.append(beta)
            else:
                print('Warning: %s not in list of controls or diseased' %samp)
                sys.exit()
            '''
            if samp[0] == 'C':    # Control
                controls.append(beta)
            elif samp[0] == 'D':    # Down
                diseased.append(beta)
            else:
                print('Warning: neither C or D')
            '''
        control_avg = float(sum(controls))/len(controls)
        diseased_avg = float(sum(diseased))/len(diseased)
        # diff_avg = diseased_avg - control_avg
        diff_avg = abs(diseased_avg - control_avg)
        x_position.append(pos)
        y_diffavg.append(diff_avg)
    
    
    plots.makeXYPlot(x_position, y_diffavg, 
                     '{0}{1}'.format('Position on Chr ', chromosome), 
                     'Absolute Difference in Betas |avgDiseased - avgControls|',
                     '{0}{1}{2}{3}'.format('Project ', project, ': beta differences in chromosome ', 
                                           chromosome),  
                     'beta_difference', 'blue')
    print('{0}{1}'.format('Time elapsed (s): ', int((time.time() - starttime))))
    # plt.show()

def PlotBetas(mongo, project, chromosome, control_samples, diseased_samples):
    '''
    Plot betas for all groups, regardless of numbers in groups since you input a 
    dictionary with arbitrary number of key:value pairs. 
    '''
    
    mongo.ensure_index(methylation_collection, 'CHR')
    mongo.ensure_index(methylation_collection, 'annotation_id')
    mongo.ensure_index(methylation_collection, 'sample_label')
    mongo.ensure_index(methylation_collection, 'start_position')
    
    query_project = {'project': project}
    query_chr = {'CHR': chromosome}
    andQuery = {'$and': [query_chr, query_project]}
    
    return_chr = {'_id': False, 'beta_value': True, 
                  'start_position': True, 'end_position': True, 
                  'sample_label': True}
    probes_chr = mongo.find(methylation_collection, 
                            andQuery, return_chr).sort('sample_label', 1)
                                                    
    position_dic = {}
    betasamp_list = []
    prev_start_pos = None
    count = 0
    for doc in probes_chr:
        if count != 0:
            if doc['start_position'] != prev_start_pos:
                position_dic[prev_start_pos] = betasamp_list
                betasamp_list = []
        betasamp_list.append((doc['beta_value'], doc['sample_label']))
        count += 1
        prev_start_pos = doc['start_position']
    position_dic[prev_start_pos] = betasamp_list
    
    
    
    '''
    plotDict = {}
    beta_pos = []
    previous_sample = None
    count = 0
    for doc in probes_chr:
        beta_pos.append((doc['start_position'], doc['beta_value']))
        # beta_pos.append((doc['beta_value'], doc['start_position']))
        if previous_sample != doc['sample_label'] and count != 0:
            beta_pos.sort()
            plotDict[doc['sample_label']] = beta_pos
            beta_pos = []
        previous_sample = doc['sample_label']
        count += 1
    beta_pos.sort()
    plotDict[doc['sample_label']] = beta_pos
    
    for sample, tuples in plotDict.iteritems():
        if sample in control_samples:
            col = 'red'
        if sample in diseased_samples:
            col = 'blue'
        pos_list = []
        betas_list = []
        for pos, betas in tuples:
            pos_list.append(pos)
            betas_list.append(betas)
        plots.makeXYPlot(pos_list, betas_list, 
                         '{0}{1}'.format('Position on Chr ', chromosome), 
                         'Beta Value', 
                         chromosome, 
                         sample,
                         col)
    plt.show()
    '''

def futureUnitTest():
    pass
    '''
    # A future unit test to see if what you get is of equal length!
    # Code not quite completed yet, so it's commented...
    
    print len(position_dic.keys())
    print probes_chr.count()/17
    
    poses_dic = sorted(position_dic.keys())
    print(poses_dic)
    
    probes_chr.rewind()
    count = 0
    poses = []
    for doc in probes_chr:
        poses.append(doc['start_position'])
    setpos = sorted(set(poses))
    print setpos
    
    print (len(poses_dic))
    print (len(setpos))
    print poses_dic == setpos
    '''


if __name__ == "__main__":
    
    for j in xrange(0, 2):
        '''
        Ask user to give a chromosome.
        '''
        chromosome_list = [str(i) for i in range(1, 24)]
        chromosome_list.append('X')
        chromosome_list.append('Y')
        chromosome_list = ['chr%s' %i for i in chromosome_list]    # Add prefix 'chr'
        while True:
            try:
                # if j == 0:
                    # chromosome = str(21)
                # elif j == 1:
                    # chromosome = str(22)
                chromosome = str(raw_input('Enter chromosome (1, 2, X, Y...): '))
                chromosome = 'chr%s' %chromosome
                if chromosome in chromosome_list:
                    break
            except:
                pass
            print('{0}{1}'.format('Invalid chromosome, choose from: ', 
                                  chromosome_list))
        
        print('Creating mongo object...')
        mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)
        print('Creating sample groups...')
        SampleGroups = CreateSampleGroups(mongo, project, feature)
        control_samples = SampleGroups[control_group_label]
        diseased_samples = SampleGroups[diseased_group_label]
        plt.subplot(2,1,j+1)
        print('Plotting beta differences...')
        PlotBetaDiff(mongo, project, chromosome, control_samples, diseased_samples, window_size)
        xmin,xmax,_,_ = plt.axis()
        plt.axis([xmin,xmax,0,1])
        print('Done for one chromosome')
    # plt.savefig('%s%s_chromosomewalk.png' %(savedirectory, project))
    plt.show()

