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
                             noSNPcpg,    # optional override to remove cpgs with snps in them
                             noSNPprobe    # optional override to remove probes with snps in them
                             ):
    '''
    This routine gets you the _ids of all projects with a given set of criteria (filter), and then returns a list representing every probe position in the array for each one.    
    '''
    filters['project'] = project_name
    filters[groupby] = {'$exists':True}
    # first find the samples of interest:

    if not groupby:
        print "no Groupby field was provided.  This query can not be run."
    print "Finding samples in project %s" % project_name
    q_returns = {"_id":1, "sampleid":1}
    q_returns[groupby] = 1
    count = connector.find("samples", filters, q_returns).count()
    print "samples matching criteria specified: ", count

    cursor = None
    compound = None

    if count < 1:
        print "looking for compound keys named ", groupby
        q_returns = {"compound." + groupby: 1}
        filters = {"project":project_name, "compound." + groupby:{'$exists':True}}
        s = connector.find("sample_groups", filters, q_returns).count()
        print "compound keys matching criteria specified: ", s
        if s < 1:
            print "Terminating - Can not process project %s with group by %s" % (project_name, groupby)
            sys.exit()
        filters = {"project":project_name}    # reset filters
        q_returns = {"compound." + groupby: 1, "_id":0}
        keys = connector.find_one("sample_groups", filters, q_returns)
        keys = keys["compound"][groupby]
        print "keys to be used: %s" % keys
        q_returns = {"_id":1, "sampleid":1}
        compound = []
        for x in keys:
            compound.append(str(x))
            q_returns[x] = 1
        cursor = connector.find("samples", filters, q_returns)
    else:
        cursor = connector.find("samples", filters, q_returns)


    ids = []
    sample_names = {}
    groups = []
    group_by_sid = {}
    for x in cursor:
        ids.append(x['_id'])
        sample_names[x['_id']] = x['sampleid']
        if compound:
            key = []
            for k in compound:
                key.append(str(x[k]))
            key = "-".join(key)
            group_by_sid[x['_id']] = key
            if key not in groups:
                groups.append(key)
        else:
            group_by_sid[x['_id']] = x[groupby]
            if x[groupby] not in groups:
                groups.append(x[groupby])

    search_criteria = {}
    if noSNPcpg:
        search_criteria["n_snpcpg"] = 0
    if noSNPprobe:
        search_criteria["n_snpprobe"] = 0

    print "accessing annotations for cursor on probe names."
    target_cursor = connector.find("annotations", search_criteria, {"targetid":1, "_id":0}).distinct("targetid")    # find all probe sample_names
    # get the results for each probe for each sample
    count = 0
    upper_outliers = 0
    lower_outliers = 0
    dual_outliers = 0
    probes_passing = 0

    # this does not match what's actually being output.
    # sb = []
    # sb.append("probe")
    # for g in groups:
    #    sb.append("%s-mean" % g)
    # for g in groups:
    #    sb.append("%s-stdev" % g)
    # sb.append("pvalue")
    # print "\t".join(sb)

    print ("probe\tmean 1\tmean 2\tstdev 1\tstdev 2\tpvalue\tgroup 1\tgroup 2")

    for i in target_cursor:    # proces probe by probe
        # print "i = ", i
        count += 1
        if 0 < limit < count:
            return
        row = {}
        data = {}
        std = {}
        mean = {}
        data_cursor = connector.find("methylation", {"pid":i, "sid": {"$in": ids}}, {"sid":1, "b":1})
        annotations_rec = connector.find_one("annotations", {"name":i}, {"n_snpcpg":1, "_id":0, "n_snpprobe":1})
        nsnpcpg = annotations_rec["n_snpcpg"]
        nsnpprobe = annotations_rec["n_snpprobe"]

        for c in data_cursor:
            sid = c['sid']

            row[sid] = c['b']
            # process groups distr. properties.
            g = group_by_sid[sid]
            if g not in data:
                data[g] = []
            data[g].append(c['b'])
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
                if not std[groups[x]] == 0 and not std[groups[y]] == 0:
                    pvalue = Kolmogorov_Smirnov.ks_test(mean[groups[x]], std[groups[x]], mean[groups[y]], std[groups[y]])
                    if pvalue >= threshold:
                        probes_passing += 1
                        print "%s\t%f\t%f\t%f\t%f\t%f\t%i\t%i\t%s\t%s" % (i, mean[groups[x]], mean[groups[y]], std[groups[x]], std[groups[y]], pvalue, nsnpcpg, nsnpprobe, groups[x], groups[y])
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
    parser.add_argument('--nosnpcpg', dest = 'noSNPcpg', action = 'store_true')
    parser.add_argument('--nosnpprobe', dest = 'noSNPprobe', action = 'store_true')
    parser.set_defaults(noSNPcpg = False)
    parser.set_defaults(noSNPprobe = False)


    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)
    mongodb = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    starttime = time.time()
    process_samples_in_order(mongodb, args.project_name, {}, args.groupby, args.limit_rows, args.threshold, args.noSNPcpg, args.noSNPprobe)
    mongodb.close()
    print('Done in %s seconds') % int((time.time() - starttime))
