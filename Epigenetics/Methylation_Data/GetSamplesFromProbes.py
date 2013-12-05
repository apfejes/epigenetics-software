'''
Created on 2013-04-18

@author: jyeung

Motivation: from a list of probes, can we plot the different samples? 
'''


import sys
import os
import time
import csv
import random
import pymongo
import matplotlib.pyplot as plt
import argparse

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
from annotUtilities import plots
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import CommonUtils.Parameters as Parameters


database_name = 'human_epigenetics'
annotation_collection = 'annotations'
methylation_collection = 'methylation'
samples_collection = 'samples'
prefix = 'humanmethylation450_beadchip_'    # prefix + TargetID = probe id
savedirectory = '/home/jyeung/Documents/Presentations/batchplots/'    # For plots

suspected_samples = ['DS09A M', 'DS01A M', 'DS04A F', 'DS06A M', 'DS10A M']
control_samples = ['C1ab F', 'C2a M', 'C2c M', 'C3a F',
                   'C4ab1 M', 'C4ab2 M', 'C5a M']
diseased_samples = ['DS02A F', 'DS03A F', 'DS05A F',
                    'DS07A M', 'DS08B F'] + ['DS09A M', 'DS01A M', 'DS04A F',
                                             'DS06A M', 'DS10A M']
control_samples = sorted(control_samples)
diseased_samples = sorted(diseased_samples)

number_of_random_probes = 50
# Suspected samples are used for coloring purposes. These may be blood contaminated.

def AskTopBtmRdn():
    '''
    Ask how many rows to skip, more rows you skip, the lower you go on table, meaning you're
    selecting for less significantly differentially methylated probes. 
    
    Outputs:
    top_or_bot:
        A string either top, bottom or random which will be used as input later to obtain top hits,
        bottom hits or random hits from hitlist.
    skip_rows:
        Depending on top_or_bot, skip number of rows when reading hitlist file. 
    '''
    tb = raw_input('Take top significant differentially methylated probes or bottom? (top/bottom/random): ')
    skip = 0
    if tb == 'top':
        skip = 1
    elif tb == 'bottom':
        skip = 800
    elif tb == 'random':
        skip = 1
    else:
        sys.exit('Only allowed "top", "bottom" or "random" as inputs, exiting...')

    return tb, skip

def GetProbesFromHits(pr_list_fname, sk_rows):
    '''
    Get list of probes from probe_list_fname, also get other values such as 
    expected difference in beta values. 
    
    Returns two values: a list of probes and a list of 'expected beta difference'
    between blood and buccal. This can be helpful for plotting because 
    if the directionality of the difference between blood and buccal could
    be informative/predictive. 
    '''
    pr_list = []
    take_top_n_hits = 50    # Take top n hits.
    c = 0
    # Grab information regarding buccal vs. blood.
    with open(pr_list_fname, 'rb') as hit_file:
        probe_reader = csv.reader(hit_file, delimiter = '\t')
        for _ in xrange(sk_rows):
            probe_reader.next()
        for row in probe_reader:
            pr_list.append(row[23])    # Probe_iD
            # delta_beta.append(row[5])    # Expected beta diff btwn buccal vs blood
            # cg_no.append(row[23])    # cg_no (x-axis of the plot)
            c += 1
            if c > take_top_n_hits:
                break
    hit_file.close()

    return pr_list

def GetRandomProbesFromHits(pr_list_fname, random_probes):
    '''
    Get a random list of probes from probe_list_fname, also get other values such as 
    expected difference in beta values. 
    
    Returns two values: a list of probes and a list of 'expected beta difference'
    between blood and buccal. This can be helpful for plotting because 
    if the directionality of the difference between blood and buccal could
    be informative/predictive. 
    '''
    p_list = []
    # count = 0
    # Grab information regarding buccal vs. blood.
    with open(pr_list_fname, 'rb') as hit_file:
        probe_reader = csv.reader(hit_file, delimiter = '\t')
        for row in probe_reader:
            p_list.append(row[23])    # ProbeID for methyl450k
            # count += 1
    hit_file.close()

    # Get 50 random probes from probe_list.
    random_indices = random.sample(xrange(0, len(probe_list)), random_probes)
    probe_list_subset = [p_list[j] for j in random_indices]

    return probe_list_subset

def GetDataFromProbeList(pr_list):
    '''
    From a list of goldengateIDs, get data from samples. 
    '''

    # Attach prefix to probename for searching in methylation collection
    probe_list_prefixed = []
    for pr in pr_list:
        probe_list_prefixed.append(''.join((prefix, pr)))
        # pr_list.append(''. join((prefix, probe_dic['cg_no'])))
    print probe_list_prefixed

    # From pr_list, get sample data. Then find number of samples.

    mongo.ensure_index(methylation_collection, 'annotation_id')    # For speed

    fQuery = {'$and': [{'annotation_id': {'$in': probe_list_prefixed}}, {'project': 'down'}]}
    rQuery = {'sample_label': True, 'start_position': True, 'beta_value': True,
              'CHR': True, '_id': False, 'annotation_id': True}
    data_cursor = mongo.find(methylation_collection, findQuery = fQuery,
                             returnQuery = rQuery).sort([('annotation_id', pymongo.ASCENDING),
                                                        ('sample_label', pymongo.ASCENDING)])
    print'%s data docs match pr_list' % data_cursor.count()

    fSampQuery = {'project': 'down'}    # 17 samples in down (unittest?)
    rSampQuery = {'patient.Total_BriefPraxis': True, 'Sample Group': True,
                  'SampleLabel': True, '_id': False}
    samples_cursor = mongo.find(samples_collection, findQuery = fSampQuery,
                                returnQuery = rSampQuery)
    samples_list = list(samples_cursor)



#     Purpose of this for loop:
#         Create a dictionary where keys are probe ids, values is list of M-values.
#         We also want to create a list of sample_ids that should match the M-values.
#
#     How I did it:
#         First, define current probe of doc.
#         Second, extend a list of M-values, but don't insert it into dictionary
#         until we have found all the M-values in that probe.
#         Third, check if current probe equals previous probe (from prev doc).
#             Note: this if only applies after the first iteration (count != 0)
#             If current probe != previous probe, we have found all M-vals for
#             that probe. So we will create a key:value pair where key is probe_id
#             and value is list of M-values.
#         Fourth, make a sample_list so we can correspond M-vals to sample. But we
#         only want to make this list once, so after we have iterated through all the
#         samples in the first probe, stop doing this.
#
    exprs_list = []
    samp_list = []
    check_samples = []
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
            # Remove humanmethylation45-_beadchip_ from probename
            probe_no_prefix = prev_probe.replace(prefix, "")
            dataDict[probe_no_prefix] = exprs_list
            exprs_list = []
            # Check if samples are in right order
            if samp_list == check_samples:
                pass
            else:
                print('Warning, samples arent in right order.')
                print samp_list
                print check_samples
            check_samples = []
            probe_count += 1
        if probe_count == 0:
            samp_list.append(doc['sample_label'])
        check_samples.append(doc['sample_label'])    # Check if samples are in right order
        exprs_list.append(doc['beta_value'])
        prev_probe = doc['annotation_id']
        data_count += 1
    probe_no_prefix = prev_probe.replace(prefix, "")
    dataDict[probe_no_prefix] = exprs_list

#     Three if conditions for sanity check. Maybe make this into unit test?

    if len(dataDict.keys()) != len(pr_list):
        print('Warning, probe lengths do not match number of keys in dictionary')
        print('Probe length: %s' % len(pr_list))
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

def EstimateBloodContamination(d_dict, samp_list, ctrl_samples,
                               disease_samples, pr_list_fname, best_hit):
    '''
    Finds average of control and then takes each diseased sample and 
    calculates difference between diseased sample and avg controls.
    
    From this average difference, estimate the expected blood contamination in 
    the samples!
    
    Use only top hit probes found from Ruiwei
    '''

    # Create dictionary with diseasedsamples as keys, avgdiff as values.
    diseased_avgdiff = {}
    for s in disease_samples:
        diseased_avgdiff[s] = []    # No values just yet

    pr_list = []

    beta_control = []
    beta_diseased = []
    print d_dict[best_hit]
    c = 0
    print samp_list
    for b in d_dict[best_hit]:
        if samp_list[c] in ctrl_samples:
            beta_control.append(b)
        elif samp_list[c] in disease_samples:
            beta_diseased.append(b)
        else:
            print('Sample in neither control or diseased')
        c += 1
    control_avg = float(sum(beta_control)) / len(beta_control)
    # diseased_avg = float(sum(beta_diseased)) / len(beta_diseased)
    for j in xrange(0, len(beta_diseased)):
        avgdiff = beta_diseased[j] - control_avg
        diseased_avgdiff[disease_samples[j]] = avgdiff
    pr_list.append(best_hit)
    print diseased_avgdiff

    buccal_avg = []
    blood_avg = []
    probe_count = 0
    with open(pr_list_fname, 'rb') as hit_file:
        probe_reader = csv.reader(hit_file, delimiter = '\t')
        for row in probe_reader:
            if row[23] in pr_list:    # row[23] is cg probename
                buccal_avg.append(float(row[3]))
                blood_avg.append(float(row[4]))
                probe_count += 1
            if probe_count >= len(pr_list):
                print('All %s probes found' % len(pr_list))
                break
    hit_file.close()

    sample_mix_tup = []
    exper_list_samps = []
    for samp, experimental_diff in diseased_avgdiff.iteritems():
        init = 0.5    # Guess the blood contamination fraction
        mix_frc = init
        c = 0
        rel_error = 1
        errorthreshold = 1e-2
        countthreshold = 1000
        error_list = []
        mix_frac_list = []
        theor_list = []
        exper_list = []
        while (abs(rel_error) > errorthreshold) and (c < countthreshold) and (mix_frc < 1) and (mix_frc > 0):

            if experimental_diff > 0:
                exper_list.append(experimental_diff)
                mix_frc = 0
                rel_error = 0    # Dangerous to say 0?
                print('%s experimental diff greater than zero, ignoring' % samp)
                break

            theor_avg_diff_list = []
            blood_weight = [j * mix_frc for j in blood_avg]
            buccal_weight = [j * (1 - mix_frc) for j in buccal_avg]
            avg_weight = [k + j for k, j in zip(blood_weight, buccal_weight)]
            for j in xrange(0, len(buccal_avg)):
                theor_avg_diff_list.append(avg_weight[j] - buccal_avg[j])
            theoretical_diff = float(sum(theor_avg_diff_list)) / len(theor_avg_diff_list)
            rel_error = float(abs(experimental_diff) - abs(theoretical_diff)) / float(experimental_diff)
            error_list.append(abs(rel_error))
            mix_frac_list.append(mix_frc)
            theor_list.append(theoretical_diff)
            exper_list.append(experimental_diff)
            if rel_error < 0 and abs(rel_error) > errorthreshold:
                # mix_frc -= 0.025
                mix_frc *= 1.05
            elif rel_error > 0 and abs(rel_error) > errorthreshold:
                # mix_frc -= 0.025
                mix_frc *= 0.95
            elif c == countthreshold - 1:
                print('Count limit reached, no solution found')
            else:
                print('%s: rel_error within threshold, error is %s.' % (samp, abs(rel_error)))
            c += 1
            # print samp, theoretical_diff, experimental_diff, rel_error, mix_frc

        sample_mix_tup.append((samp, mix_frc, rel_error))
        exper_list_samps.append(exper_list[0])

    return sample_mix_tup

def PlotSuspectedContamination(sample_mix_tup, probe):
    '''TODO: missing docstring'''
    sam = [j[0] for j in sample_mix_tup]
    fra = [j[1] for j in sample_mix_tup]
    x = range(0, len(samps))
    plt.bar(x, fracs, color = 'b', align = 'center')
    plt.ylabel('Predicted fraction of blood in buccal sample', fontsize = 15)
    plt.title('Predicted blood fraction using %s' % probe, fontsize = 15)
    plt.xticks(x, samps, fontsize = 10, rotation = 45)
    _, xmax, _, _ = plt.axis()
    plt.axis([-0.5, xmax, 0, 1])
    return sam, fra

def CalculateAvgContamination(samp_list, fr_list):
    '''Calculate the average contamination'''
    sample = samp_list[0]    # List in each index should contain same list.
    fracs_by_samps = []    # Rearrange fr_list so each index is its own list
    for k in xrange(0, len(sample)):
        fracs_by_samps.append([j[k] for j in fr_list])

    # Calculate mean and variance.
    mean_list = []
    stderr_list = []
    for samp_fracs in fracs_by_samps:
        n = 0
        Sum = 0
        Sum_sqr = 0
        for frac in samp_fracs:
            n += 1
            Sum += frac
            Sum_sqr += frac * frac

        stderr_list.append(((Sum_sqr - ((Sum * Sum) / n)) / (n - 1)) ** 0.5)
        mean_list.append(Sum / n)

    x = range(0, len(sample))
    plt.bar(x, mean_list, align = 'center', yerr = stderr_list)
    plt.ylabel('Average predicted fraction of blood in buccal sample', fontsize = 15)
    plt.title('Predicted blood fraction: Averaged over 4 probes', fontsize = 15)
    plt.xticks(x, sample, fontsize = 10, rotation = 45)
    _, xmax, _, _ = plt.axis()
    plt.axis([-0.5, xmax, 0, 1])

    return sample, fracs




def PlotBetasInProbes(d_dict, samp_list, suspect_samples, pr_list, plot_title):
    '''
    From data_dictionary of probe:datalist pairs, plot the datalist against probe.
    Inputs:
        d_dict: probe:datalist pair. Unordered, so probe_list is used to make sure 
            it plots with the same order as probe_list. 
        samp_list: list of samples, tells the datalist which data corresponds
            to which sample. 
        suspect_samples: samples that are 'suspected' and will be colored red. 
            Suspected could be: if you think some samples are contaminated, you would 
            color those samples red, and everything else a different color for
            cmoparison purposes.
        pr_list: list of probes to make sure data_dict plots in same order as 
            probe_list. 
        plot_title: title of plot. 
    '''

    # Set plotcolors. Color suspected samples 'red'
    plotcolors = []
    for s in samp_list:
        if s in suspect_samples:
            plotcolors.append('red')
        else:
            plotcolors.append('blue')

    x_list = []    # For plotting
    for j in xrange(len(samp_list)):
        y_list = []    # Reset for every i
        for pr in pr_list:
            if j == 0:
                x_list.append(pr)
            y_list.append(d_dict[pr][j])

#         for probe, val_list in data_dict.iteritems():
#             if i == 0:
#                 # Remove humanmethylation450_beadship_ prefix with 'replace'
#                 x_list.append(probe.replace(prefix, ""))
#             y_list.append(val_list[i])

        plots.makeXYPlot(range(len(x_list)), y_list, 'probe ID', 'Beta-value', plot_title,
                         samp_list[j], plotcolors[j])

    plt.xticks(range(len(x_list)), x_list, size = 'small', rotation = 45)
    plt.title(plot_title, y = 0.92, fontsize = 20)

    # Adjust x-axis, concatonate an expected delta beta value to x-axis to
    # see expected difference between blood and buccal
#     for tup in suffix_to_label_tuple:
#         if tup[0] in x_list:
#             index_x = x_list.index(tup[0])
#             x_list[index_x] = '_'.join((x_list[index_x], tup[1]))
#     plt.xticks(range(len(x_list)), x_list, size='small', rotation=90)

    return x_list

def PlotBuccalVsBlood(pr_list_fname, probes_to_plot, mix_frc):
    '''TODO: Missing docstring'''
    subtitle = 'Avg Beta Values of Buccal and Contaminated Buccal (%s fraction blood)' % mix_frc
    beta_buccal = []
    beta_blood = []
    cg_no = []
    number_of_probes = len(probes_to_plot)
    probe_count = 0
    # Grab information regarding buccal vs. blood.
    with open(pr_list_fname, 'rb') as hit_file:
        probe_reader = csv.reader(hit_file, delimiter = '\t')
        for row in probe_reader:
            if row[23] in probes_to_plot:
                buccal_avg = float(row[3])
                blood_avg = float(row[4])
                beta_buccal.append(buccal_avg)    # Average buccal beta val
                # Imagine it is a blood/buccal mixture...
                beta_blood.append((1 - mix_frc) * buccal_avg + mix_frc * blood_avg)
                cg_no.append(row[23])    # cg_no (probeID)
                probe_count += 1
            if probe_count >= number_of_probes:
                print('All indicated probes found')
                break
    hit_file.close()
    plots.makeXYPlot(range(len(cg_no)), beta_buccal, '', 'Beta-value', None,
                     'buccal', 'blue')
    plots.makeXYPlot(range(len(cg_no)), beta_blood, '', 'Beta-value', None,
                     '%s blood, %s buccal' % (mix_frc, 1 - mix_frc), 'red')
    plt.title(subtitle, fontsize = 20)
    plt.xticks(range(len(cg_no)), cg_no, size = 'small', rotation = 45)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("probelist", help = "The file name of the probe list", type = str)
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)
    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)

    mongo = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    top_or_bot, skip_rows = AskTopBtmRdn()
    starttime = time.time()

    # Get dictionary containing probe_list and beta_difference between blood and buccal
    # If you're looking for a random set of probes, use the modified function.
    # cg_no is a type of Probe ID.


    if top_or_bot == 'random':
        probe_list = GetRandomProbesFromHits(args.probelist, number_of_random_probes)
    elif (top_or_bot == 'top') or (top_or_bot == 'bottom'):
        probe_list = GetProbesFromHits(args.probelist, skip_rows)
    else:
        print('Neither top, bottom, or random... dont know what to do.')
        sys.exit()

    # Get dictionary containing a data dictionary and a sample list
    data_and_sample_dic = GetDataFromProbeList(probe_list)

    # Now let's plot our data.
    data_dict = data_and_sample_dic['data_dictionary']
    sample_list = data_and_sample_dic['sample_list']

    title = 'Beta Values of Buccal Samples in Down Syndrome Study, Colored by PCA Cluster'

    # Because probe_list was from goldengate, may not match all in methyl450.
    # so we readjust probe_list to make sure only the matched probes are used.
    # this is important so we can plot the probes in order from most to least
    # significant

    good_indices = []
    for i, p in enumerate(probe_list):
        if p in data_dict.keys():
            good_indices.append(i)
    matched_probe_list = [probe_list[i] for i in good_indices]

    # Estimate blood contamination
    # top_hit = 'cg23497683'    # the top hit
    # top_hit = 'cg02285920'    # another top-ish hit
    # top_hit = 'cg03583857'    # another top-ish hit
    # top_hit = 'cg13984563'    # another top-ish hit
    tophits = ['cg23497683', 'cg02285920', 'cg03583857', 'cg13984563']
    count = 0
    samps_list = []
    fracs_list = []
    for top_hit in tophits:
        count += 1
        samp_mix = EstimateBloodContamination(data_dict, sample_list, control_samples,
                                              diseased_samples, args.probelist, top_hit)
        plt.subplot(2, 2, count)
        samps, fracs = PlotSuspectedContamination(samp_mix, top_hit)
        samps_list.append(samps)
        fracs_list.append(fracs)

    plt.show()
    plt.clf()

    CalculateAvgContamination(samps_list, fracs_list)
    plt.show()
    plt.clf()

    plt.subplot(2, 1, 2)
    probes_plotted = PlotBetasInProbes(data_dict, sample_list,
                                       suspected_samples, matched_probe_list, title)

    # Long code to remove 'humanmethylation450_beadchip_ from keyname

    plt.subplot(2, 1, 1)
    mix_frac = 0.25
    PlotBuccalVsBlood(args.probelist, probes_plotted, mix_frac)
    mongo.close()
    print('Time elapsed: %s seconds' % int(time.time() - starttime))
    plt.show()



