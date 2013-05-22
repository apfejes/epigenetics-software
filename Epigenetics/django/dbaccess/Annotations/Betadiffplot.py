'''
Created on 2013-05-20

@author: sperez
Edited from "WalkAlongChromosome.py"  written by jyeung
'''

import sys
import os
import time

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector

starttime = time.time()
database_name = 'human_epigenetics'
# database_name = 'jake_test'
annotation_collection = 'annotations'
methylation_collection = 'methylation'
sample_collection = 'samples'
window_size = 1   # For binning purposes

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
    count = 0
    for doc in probes_chr:
        if count%10000 == 0:
            print('%s of %s documents analyzed.' %(count, probes_chr.count()))
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
        control_avg = float(sum(controls))/len(controls)
        diseased_avg = float(sum(diseased))/len(diseased)
        diff_avg = abs(diseased_avg - control_avg)
        x_position.append(pos)
        y_diffavg.append(diff_avg)
    
    
    makeXYPlot(x_position, y_diffavg, 
                     '{0}{1}'.format('Position on Chr ', chromosome), 
                     'Absolute Difference in Betas |avgDiseased - avgControls|',
                     '{0}{1}{2}{3}'.format('Project ', project, ': beta differences in chromosome ', 
                                           chromosome),  
                     'beta_difference', 'blue')
    print('{0}{1}'.format('Time elapsed (s): ', int((time.time() - starttime))))

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



from svgwrite.drawing import Drawing
from svgwrite.path import Path


def makelinepath(X,Y):
    smooth = False
    offset =  X[0]
    invertby = max(Y)
    
    print smooth, X[0], offset, invertby
    X = [round(float(item-offset)/20000,3)+20 for item in X]
    
    Y = [round((invertby-item)*1000,2)+20 for item in Y]
    
    d = "M"+str(X[0])+","+str(Y[0])+" "+str(X[1])+","+str(Y[1])
    if smooth: d = d +"S"
    
    for i in range(2,len(X)):
        d=d+(" "+str(X[i])+","+str(Y[i]))
    print "The path:", d
    return d, str(X[-1]), str(max(Y))

def makeXYPlot(x, y, xLabel, yLabel, title, sampLabel=None, color='blue'):
    """ Make a plot from a list of x, list of y. 
    xLabel, yLabel = the labels for the x and y axis respectively
    title = the top title for the plot
    sampLabel=sample labels
    """

    #Drawing a methylation plot
    #d is the list of coordinates with commands such as
    #M for "move to' to initiate curve and S for smooth curve
    d, length, height = makelinepath(x,y)
    gene = Drawing("SVGs/betadiffchr21.svg", size=(str(float(length)+10) + "mm", str(float(height)+10)+ "mm"), viewBox=("0 0 "+str(float(length)+10)+" "+str(float(height)+10)), preserveAspectRatio="xMinYMin meet")
    
    gene.add(Path(stroke = "blue", fill = "none", d = d))
    
    gene.save()
    print "The methylation data is ready to be viewed." 
    
    

if __name__ == "__main__":
    project = 'down'
    feature = 'Sample Group'
    control_group_label = 'Control'
    diseased_group_label = 'DS'

    #Choose which chromosome to print and format it as "chr#"
    chromosome = "chr21"

    print('Creating mongo object...')
    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)
    print('Creating sample groups...')
    SampleGroups = CreateSampleGroups(mongo, project, feature)
    control_samples = SampleGroups[control_group_label]
    diseased_samples = SampleGroups[diseased_group_label]
    print('Plotting beta differences...')
    PlotBetaDiff(mongo, project, chromosome, control_samples, diseased_samples, window_size)
    print('Done for %s chromosome' %chromosome)

