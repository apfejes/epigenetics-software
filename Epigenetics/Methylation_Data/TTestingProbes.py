'''
Created on 2013-04-24

@author: jyeung
'''

import sys
import os
import time
from scipy import stats
import matplotlib.pyplot as plt
import numpy as np    # For density plot
from scipy.stats import gaussian_kde    # for density plot

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
from WalkAlongChromosome import CreateSampleGroups
from annotUtilities import plots

database_name = 'human_epigenetics'
methylation_collection = 'methylation'
samples_collection = 'samples'
savedirectory = '/home/jyeung/Documents/Presentations/batchplots/'

'''
# Settings for kollman listeria project
project = 'kollman'
feature = 'stimulation'
control_label = []    # Will define in the 'main' section
diseased_label = []    # Will define in the 'main' section

# Settings for down syndrome project
project = 'down'
feature = 'Sample Group'
control_label = 'Control'    # for down
diseased_label = 'DS'    # for down 
'''

FDR = 0.05

def FindDiffProbes(project, group_control, group_diseased):
    '''
    Find differentially methylated probes 
    '''
    mongo.ensure_index(methylation_collection, 'annotation_id')
    mongo.ensure_index(methylation_collection, 'sample_label')
    
    # query_project = {'project': project}
    query_project = {'$and': [{'project': project}, {'annotation_id': {'$exists': True}}]}
    
    return_query = {'_id': False, 
                    'exprs_value': True, 'beta_value': True, 
                    'sample_label': True, 'annotation_id': True}
    
    '''
    control_cursor = mongo.find(methylation_collection,
                                {'$and': [query_project, query_control]}, 
                                return_query).sort('annotation_id', 1)
    diseased_cursor = mongo.find(methylation_collection,
                                 {'$and': [query_project, query_diseased]}, 
                                 return_query).sort('annotation_id', 1)
    exprs_control = []
    exprs_diseased = []
    p_vals = []
    control_count = 0
    diseased_count = 0
    for control_doc in control_cursor:
        control_count += 1
        exprs_control.append(control_doc['exprs_value'])
        if control_count % len(group_control) == 0:
            for i in xrange(diseased_count, diseased_count + len(group_diseased)):
                diseased_count += 1
                exprs_diseased.append(diseased_cursor[i]['exprs_value'])
            _, p = stats.ttest_ind(exprs_control, exprs_diseased)
            p_vals.append((control_doc['annotation_id'], p))
            exprs_control = []
            exprs_diseased = []
        if control_count % 10000 == 0:
            break
    print len(p_vals)
    print time.time()-starttime
    '''
    data_cursor = mongo.find(methylation_collection, 
                             query_project, return_query).sort('annotation_id', 1)
    
    count = 0
    probe_pval = []
    exprs_control = []
    betas_control = []
    exprs_diseased = []
    betas_diseased = []
    probe_beta_control = {}
    probe_beta_diseased = {}
    for doc in data_cursor:
        if count == 0:
            prev_probe = doc['annotation_id']
            
        if prev_probe != doc['annotation_id']:
            # t-test two samples once we've iterated all samples in probe
            _, p = stats.ttest_ind(exprs_control, exprs_diseased)
            probe_pval.append((prev_probe, p))
            exprs_control = []
            exprs_diseased = []
            probe_beta_control[prev_probe] = betas_control
            probe_beta_diseased[prev_probe] = betas_diseased
            betas_control = []
            betas_diseased = []
            
        if doc['sample_label'] in group_control:
            exprs_control.append(doc['exprs_value'])
            betas_control.append(doc['beta_value'])
        
        elif doc['sample_label'] in group_diseased:
            exprs_diseased.append(doc['exprs_value'])
            betas_diseased.append(doc['beta_value'])
        
        else:
            print('Sample in neither control or diseased group...')
            sys.exit()
        
        prev_probe = doc['annotation_id']
        count += 1
        
        '''
        # Code for quickly scanning through subset of docs and plot.
        # For testing purposes. 
        if count%500000 == 0:
            break
        '''
           
    # Iterated all samples, do one more t-test for the last probe. 
    # t-test two samples once we've iterated all samples in probe
    _, p = stats.ttest_ind(exprs_control, exprs_diseased)
    # probe_pval[prev_probe] = p
    probe_pval.append((prev_probe, p))
    exprs_control = []
    exprs_diseased = []
    probe_beta_control[prev_probe] = betas_control
    probe_beta_diseased[prev_probe] = betas_diseased
    betas_control = []
    betas_diseased = []

    return sorted(probe_pval, key=lambda tup: tup[1]), probe_beta_control, probe_beta_diseased

def FindPValThreshold(pvals, FDR):
    count = 0
    m = len(pvals)
    for p in pvals:
        count += 1
        if FDR * count / m > p:
            pass
        else:
            threshold = count
            break
    return threshold
        
def AdjustPValsBH(pvals):
    qvals = []
    count = 0
    m = len(pvals)
    for p in pvals:
        count += 1
        qvals.append(p*m / count)
        # probes_q_vals[probe] = pval * len(probes_p_vals) / count
        # probes_q_vals.append((probe, (pval * len(probes_p_vals) / count)))
        # Ensure the q-values are ascending with p-values.
    '''
    # Code to try to ensure qvals increase with pvals, apparently 
    # this is not as trivial as it seems... or maybe I am approaching 
    # the problem incorrectly...
    
    min_q = min(qvals[1:len(qvals)])
    min_q_index = qvals.index(min_q)
    plt.subplot(2, 2, 1)
    plt.plot(range(0, len(qvals)), qvals)
    if qvals[0] > min_q:
        for i in xrange(0, min_q_index):
            qvals[i] = min_q
    else:
        for i in xrange(1, min_q_index):
            qvals[i] = min_q
    '''
    density = gaussian_kde(pvals)
    xs = np.linspace(0, 1, 100)
    density.covariance_factor = lambda: 0.25    # Adjust bandwidth of density
    density._compute_covariance()
    
    plt.plot(xs, density(xs))
    plt.title('Distribution of Unadjusted P-Values', fontsize=20)
    plt.xlabel('Unadjusted P-Value', fontsize=15)
    plt.ylabel('Density', fontsize=15)
    plt.savefig('%s%s_pval_distribution.png' %(savedirectory, project))
    plt.clf()
    # plt.show()
    
    # plt.subplot(2, 2, 2)
    plt.plot(range(0, len(qvals)), qvals)
    plt.title('BH-adjusted P-Value by Rank: Untweaked', fontsize=20)
    plt.xlabel('Ranked Probe', fontsize=15)
    plt.ylabel('BH-Adjusted P-Value: Untweaked', fontsize=15)
    xmin,xmax,_,_ = plt.axis()
    plt.axis([xmin, xmax, 0, 1.1])
    plt.savefig('%s%s_qvals_untweaked.png' %(savedirectory, project))
    plt.clf()
    # plt.show()
    
    return qvals
    
def PlotHits(control_betas_dic, diseased_betas_dic, hit_tuple):
    xlabs = ['control', 'diseased']
    yLabel = 'Beta value'
    count = 1
    for h, pval in hit_tuple:
        print h
        plt.subplot(2, 2, count)
        y_control = control_betas_dic[h]
        x_control = [1] * len(y_control)
        y_diseased = diseased_betas_dic[h]
        x_diseased = [2] * len(y_diseased)
        title = '%s, pval=%.3e' %(h[len(h)-10:len(h)], pval)
        plots.makeScatter(x_control, y_control, xlabs, yLabel, title)
        # _,_,yc1,yc2 = plt.axis()
        plots.makeScatter(x_diseased, y_diseased, xlabs, yLabel, title)
        # _,_,yd1,yd2 = plt.axis()
        # ymin = min([yc1, yd1])
        # ymax = max([yc2, yd2])
        # plt.axis([0,3,ymin,ymax])    # To scale y-axis by datapoints.
        plt.axis([0, 3, 0, 1])    # To force y-axis [0, 1]
        count += 1
    plt.savefig('%s%s_hits.png' %(savedirectory, project))
    plt.clf()
    # plt.show()
    
if __name__ == "__main__":
    for i in xrange(0, 2):
        print i
        if i == 0:
            # Settings for kollman listeria project
            project = 'kollman'
            feature = 'stimulation'
            control_label = []    # Will define in the 'main' section
            diseased_label = []    # Will define in the 'main' section
        
        elif i == 1:
            # Settings for down syndrome project
            project = 'down'
            feature = 'Sample Group'
            control_label = 'Control'    # for down
            diseased_label = 'DS'    # for down 
        
        else:
            sys.exit('Two iterations completed, done')
        
        starttime = time.time()
        mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)
        sample_groups = CreateSampleGroups(mongo, project, feature)
        
        diseased = []
        control = []
        '''
        For kollman:
        Rearrange sample_groups so Cord and Listeria is one group, everybody else is another group
        '''
        if project == 'kollman':
            # cord_listeria = ['16 Cord 2 Lm', '18 Cord 3 Lm']
            diseased = ['16 Cord 2 Lm', '18 Cord 3 Lm']
            for sample_label in sample_groups.values():
                for item in sample_label:
                    # if item not in cord_listeria:
                    if item not in diseased:
                        control.append(item)
        
        else:
            control = sample_groups[control_label]
            diseased = sample_groups[diseased_label]
        
        # probes_p_vals, control_dic, diseased_dic = FindDiffProbes(project, control, cord_listeria)
        probes_p_vals, control_dic, diseased_dic = FindDiffProbes(project, control, diseased)
        print('Done finding diff probes, elapsed time: %.0f s' %(time.time()-starttime))
        pvals = [i[1] for i in probes_p_vals]
        qvals = AdjustPValsBH(pvals)
        print('Done adjusting pvals. time: %.0f s' %(time.time()-starttime))
        threshold = FindPValThreshold(pvals, FDR)
        print('There are %s probes that are significant above FDR of %s' %(threshold, FDR))
        # top 4 hits
        hit_tuple = probes_p_vals[0:4]
        # hits = [i[0] for i in hit_tuple]
        print('Plotting top 4 hits, time: %.0f seconds' %(time.time()-starttime))
        PlotHits(control_dic, diseased_dic, hit_tuple)
