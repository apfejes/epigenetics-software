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
from numpy.lib.utils import deprecate

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
from WalkAlongChromosome import CreateSampleGroups
from annotUtilities import plots
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import CommonUtils.Parameters as Parameters

methylation_collection = 'methylation'
samples_collection = 'samples'
savedirectory = '/home/jyeung/Documents/Presentations/batchplots/'

FDR = 0.05

@deprecate
def FindDiffProbes(project_name, group_control, group_diseased):
    '''
    Find differentially methylated probes 
    '''
    mongo.ensure_index(methylation_collection, 'annotation_id')
    mongo.ensure_index(methylation_collection, 'sample_label')

    query_project = {'$and': [{'project': project_name}, {'annotation_id': {'$exists': True}}]}

    return_query = {'_id': False,
                    'exprs_value': True, 'beta_value': True,
                    'sample_label': True, 'annotation_id': True}

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


        # Code for quickly scanning through subset of docs and plot.
        # For testing purposes.
        # if count%500000 == 0:
        #    break

    # Iterated all samples, do one more t-test for the last probe.
    # t-test two samples once we've iterated all samples in probe
    _, p = stats.ttest_ind(exprs_control, exprs_diseased)
    probe_pval.append((prev_probe, p))
    exprs_control = []
    exprs_diseased = []
    probe_beta_control[prev_probe] = betas_control
    probe_beta_diseased[prev_probe] = betas_diseased
    betas_control = []
    betas_diseased = []

    return sorted(probe_pval, key = lambda tup: tup[1]), probe_beta_control, probe_beta_diseased

def FindPValThreshold(pvalues, Fdr):
    '''TODO:missing doc string'''
    count = 0
    m = len(pvalues)
    for p in pvalues:
        count += 1
        if Fdr * count / m > p:
            pass
        else:
            t = count
            break
    return t

def AdjustPValsBH(pvalues):
    '''TODO:missing doc string'''
    qvalues = []
    count = 0
    m = len(pvalues)
    for p in pvalues:
        count += 1
        qvalues.append(p * m / count)

    density = gaussian_kde(pvalues)
    xs = np.linspace(0, 1, 100)
    density.covariance_factor = lambda: 0.25    # Adjust bandwidth of density
    density._compute_covariance()

    plt.plot(xs, density(xs))
    plt.title('Distribution of Unadjusted P-Values', fontsize = 20)
    plt.xlabel('Unadjusted P-Value', fontsize = 15)
    plt.ylabel('Density', fontsize = 15)
    plt.savefig('%s%s_pval_distribution.png' % (savedirectory, project))
    plt.clf()

    plt.plot(range(0, len(qvalues)), qvalues)
    plt.title('BH-adjusted P-Value by Rank: Untweaked', fontsize = 20)
    plt.xlabel('Ranked Probe', fontsize = 15)
    plt.ylabel('BH-Adjusted P-Value: Untweaked', fontsize = 15)
    xmin, xmax, _, _ = plt.axis()
    plt.axis([xmin, xmax, 0, 1.1])
    plt.savefig('%s%s_qvals_untweaked.png' % (savedirectory, project))
    plt.clf()

    return qvalues

def PlotHits(control_betas_dic, diseased_betas_dic, hit_tuples):
    '''TODO:missing doc string'''
    xlabs = ['control', 'diseased']
    yLabel = 'Beta value'
    count = 1
    for h, pval in hit_tuples:
        print h
        plt.subplot(2, 2, count)
        y_control = control_betas_dic[h]
        x_control = [1] * len(y_control)
        y_diseased = diseased_betas_dic[h]
        x_diseased = [2] * len(y_diseased)
        title = '%s, pval=%.3e' % (h[len(h) - 10:len(h)], pval)
        plots.makeScatter(x_control, y_control, xlabs, yLabel, title)
        plots.makeScatter(x_diseased, y_diseased, xlabs, yLabel, title)
        plt.axis([0, 3, 0, 1])    # To force y-axis [0, 1]
        count += 1
    plt.savefig('%s%s_hits.png' % (savedirectory, project))
    plt.clf()

if __name__ == "__main__":
    for i in xrange(0, 2):
        if i == 0:
            # Settings for kollman listeria project
            project = 'kollman'
            feature = 'stimulation'
            control_label = []
            diseased_label = []

        elif i == 1:
            # Settings for down syndrome project
            project = 'down'
            feature = 'Sample Group'
            control_label = 'Control'    # for down
            diseased_label = 'DS'    # for down

        else:
            sys.exit('Two iterations completed, done')

        print('Finding differentially methylated probes in %s' % project)
        starttime = time.time()

        p = Parameters.parameter()
        mongo = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
        sample_groups = CreateSampleGroups(mongo, project, feature)

        diseased = []
        control = []
        # For kollman:
        # Rearrange sample_groups so Cord and Listeria is one group, everybody else is another group
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

        probes_p_vals, control_dic, diseased_dic = FindDiffProbes(project, control, diseased)
        print('Done finding diff probes, elapsed time: %.0f s' % (time.time() - starttime))

        pvals = [i[1] for i in probes_p_vals]
        qvals = AdjustPValsBH(pvals)
        print('Done adjusting pvals. time: %.0f s' % (time.time() - starttime))

        threshold = FindPValThreshold(pvals, FDR)
        print('There are %s probes that are significant above FDR of %s' % (threshold, FDR))

        # top 4 hits
        hit_tuple = probes_p_vals[0:4]
        print('Plotting top 4 hits, time: %.0f seconds' % (time.time() - starttime))

        PlotHits(control_dic, diseased_dic, hit_tuple)
