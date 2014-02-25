'''
Created on Jan 29, 2014

@author: apfejes
'''
import argparse
import time
import os
import sys
import numpy

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
while ("MongoDB" in _root_dir):
    _root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
from CommonUtils import Parameters
import Mongo_Connector
from CommonUtils.Statistics import Kolmogorov_Smirnov, lower_Qtest, upper_Qtest


def process_samples_in_order(connector,    # mongo connector
                             project_name,    # name of project to analyze
                             filters,    # optional filters
                             groupby,    # field to group by
                             limit,    # optional limit to number of probes to process.
                             threshold,    # optional override to threshold at which probes are kept.
                             ):
    '''
    This routine gets you the _ids of all projects with a given set of criteria (filter), and then returns a list representing every probe position in the array for each one.    
    '''
    filters['project'] = project_name
    # first find the samples of interest:

    if not groupby:
        print "no Groupby field was provided.  This query can not be run."


    print "Finding samples in project %s" % project_name
    q_returns = {"_id":1, "sampleid":1}
    q_returns[groupby] = 1
    cursor = connector.find("samples", filters, q_returns)
    ids = []
    sample_names = {}
    groups = []
    group_by_sid = {}
    for x in cursor:
        ids.append(x['_id'])
        sample_names[x['_id']] = x['sampleid']
        group_by_sid[x['_id']] = x[groupby]
        if x[groupby] not in groups:
            groups.append(x[groupby])


    print "accessing annotations for cursor on probe names."
    target_cursor = connector.distinct("annotations", "targetid")    # find all probe sample_names
    # get the results for each probe for each sample
    count = 0
    upper_outliers = 0
    lower_outliers = 0
    dual_outliers = 0
    probes_passing = 0

    sb = []
    sb.append("probe")
    for g in groups:
        sb.append("%s-mean" % g)
    for g in groups:
        sb.append("%s-stdev" % g)
    sb.append("pvalue")
    print "\t".join(sb)

    for i in target_cursor:    # proces probe by probe
        # print "i = ", i
        count += 1
        if limit > 0 and count > limit:
            return
        row = {}
        data = {}
        std = {}
        mean = {}
        data_cursor = connector.find("methylation", {"probeid":i, "sampleid": {"$in": ids}}, {"sampleid":1, "beta":1})

        for c in data_cursor:
            sid = c['sampleid']

            row[sid] = c['beta']
            # process groups distr. properties.
            g = group_by_sid[sid]
            if g not in data:
                data[g] = []
            data[g].append(c['beta'])
        if data == {}:
            # print "No values found for probe ", i
            continue

        for g in groups:
            # calculate s and m
            t1, v1 = lower_Qtest(data[g], "Q99")
            t2, v2 = upper_Qtest(data[g], "Q99")
            if t2 and t1:    # can't trim both.
                # print "lower and upper outliers found: (probe %s) - not filtered" % (i)
                dual_outliers += 1
            elif t1:
                data[g] = v1
                # print "lower outlier found: (probe %s)" % (i)
                lower_outliers += 1
            elif t2:
                data[g] = v2
                # print "upper outlier found: (probe %s)" % (i)
                upper_outliers += 1
            try:
                std[g] = numpy.std(data[g])
                mean[g] = numpy.mean(data[g])
            except KeyError as e:
                print "KEY ERROR EXCEPTION FOUND:", e
                print "i", i
                print "std", std
                print "mean", mean



        for x in range(len(groups)):    # do pairwise comparison
            for y in range(x + 1, len(groups)):
                pvalue = Kolmogorov_Smirnov.ks_test(mean[groups[x]], std[groups[x]], mean[groups[y]], std[groups[y]])
                if pvalue >= threshold:
                    probes_passing += 1
                    print "%s\t%f\t%f\t%f\t%f\t%f\t%s & %s" % (i, mean[groups[x]], mean[groups[y]], std[groups[x]], std[groups[y]], pvalue, groups[x], groups[y])
                    # print "   means %s | %f %f" % (g, mean[groups[x]], mean[groups[y]])
                    # print "   stdv. %s | %f %f" % (g, std[groups[x]], std[groups[y]])
                    # print "   group %s vs %s --> pval = %f" % (groups[x], groups[y], pvalue)
        # print "%s = %s" % (i, v)
        if count % 10000 == 0:
            print "Row %i" % count    # for debugging
    # wht's missing and the sorting'
    print "###############################"
    print "          Report"
    print "###############################"
    print ""
    print "lower outliers eliminated: ", lower_outliers
    print "upper outliers eliminated: ", upper_outliers
    print "probes with dual outliers: ", dual_outliers
    print "probes passing threshold:  ", probes_passing



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", help = "Name of Project to Export", type = str)
    parser.add_argument("groupby", help = "Name of field to group by", type = str)
    parser.add_argument("-limit_rows", help = "An optional integer limit to the number of probes to process", type = int, default = -1)
    parser.add_argument("-threshold", help = "An float value below which ks test results will be discarded [default = 0.95]", type = float, default = 0.95)
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)

    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)
    mongodb = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    starttime = time.time()
    process_samples_in_order(mongodb, args.project_name, {}, args.groupby, args.limit_rows, args.threshold)
    mongodb.close()
    print('Done in %s seconds') % int((time.time() - starttime))
