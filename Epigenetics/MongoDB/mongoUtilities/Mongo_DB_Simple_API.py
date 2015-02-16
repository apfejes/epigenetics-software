"""
Created on Jan 29, 2014

@author: apfejes
"""

import argparse
import time
import os
import sys
import gzip
import numpy

# where the current file is
_cur_dir = os.path.dirname(os.path.realpath(__file__))
_root_dir = os.path.dirname(_cur_dir)
while "MongoDB" in _root_dir:
    _root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
from CommonUtils import Parameters
import Mongo_Connector
from Statistics import Kolmogorov_Smirnov


def process_samples_in_order(connector, project_name, filters, groupby, limit):
    """ This routine gets you the _ids of all projects with a given set of
        criteria (filter), and then returns a list representing every probe
        position in the array for each one.
    """
    filters['project'] = project_name
    # first find the samples of interest: 00000000000000000000000000000000000000

    if not groupby:
        print "no Groupby field was provided.  This query can not be run."

    q_returns = {"_id": 1, "sampleid": 1, "groupby": 1}
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

    target_cursor = connector.distinct("annotations", "targetid")
    # find all probe sample_names
    # get the results for each probe for each sample
    count = 0
    '''write out headers '''

    ''' process probe-by-probe'''

    for i in target_cursor:
        # print "i = ", i
        count += 1
        if count > limit:
            return
        row = {}
        data = {}
        std = {}
        mean = {}
        data_cursor = connector.find("methylation",
                                     {"pid": i, "sid": {"$in": ids}},
                                     {"sid": 1, "b": 1})

        for c in data_cursor:
            sid = c['sid']

            row[sid] = c['b']
            # process groups distr. properties.
            g = group_by_sid[sid]
            if g not in data:
                data[g] = []
            data[g].append(c['b'])
        print "Probe %s", i
        for g in groups:
            # calculate s and m
            std[g] = numpy.std(data[g])
            mean[g] = numpy.mean(data[g])
            print "   %s | %f %f" % (g, std[g], mean[g])
        '''do pairwise comparison'''

        for x in range(len(groups)):
            for y in range(x, len(groups)):
                pvalue = Kolmogorov_Smirnov.ks_test(mean[x], std[x],
                                                    mean[y], std[y])
                print "   group %s vs %s --> pval = %f" % (groups[x],
                                                           groups[y], pvalue)
        # print "%s = %s" % (i, v)
        if count % 10000 == 0:
            print "Row %i" % count    # for debugging
    # what's missing and the sorting'


def export_samples_as_table(connector, project_name, filters, filename):
    """
    This routine gets you the _ids of all projects with a given set of
    criteria (filter), and then returns a list representing every probe
    position in the array for each one.
    """
    filters['project'] = project_name
    # first find the samples of interest:
    cursor = connector.find("samples", filters, {"_id": 1, "sampleid": 1})
    ids = []
    names = {}
    for x in cursor:
        ids.append(x['_id'])
        names[x['_id']] = x['sampleid']

    # find all probe names
    target_cursor = connector.distinct("annotations", "targetid")

    f = gzip.open(filename, "wb", 9)

    # get the results for each probe for each sample
    # print "names:", names
    count = 0
    header = "\t".join([names[n] for n in names])
    f.write("probe\t" + header)
    f.write("\n")
    for i in target_cursor:
        # print "i = ", i
        count += 1
        row = {}
        strlist = []
        data_cursor = connector.find("methylation",
                                     {"pid": i, "sid": {"$in": ids}},
                                     {"sid": 1, "b": 1})
        for c in data_cursor:
            row[c['sid']] = c['b']
        for n in names:
            if n in row:
                strlist.append("%.8f" % row[n])
            else:
                strlist.append("NA")
        f.write("%s\t" % i)
        v = '\t'.join(strlist)
        f.write(v)
        f.write("\n")
        # print "%s = %s" % (i, v)
        if count % 10000 == 0:
            print "Row %i" % count    # for debugging
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name",
                        help="Name of Project to Export", type=str)
    parser.add_argument("filename",
                        help="Full path and name of file to create, where the "
                             "methylation export data will be placed",
                        type=str,
                        default=None)
    parser.add_argument("-limit",
                        help="An optional integer limit to the number "
                             "of probes to process",
                        type=int, default=None)
    parser.add_argument("-dbconfig",
                        help="An optional file to specify the database "
                             "location - default is database.conf in "
                             "MongoDB directory",
                        type=str, default=None)
    parser.add_argument("-dbname",
                        help="name of the Database in the Mongo implementation "
                             "to use - default is provided in the "
                             "database.conf file specified",
                        type=str, default=None)
    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)
    mongodb = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'),
                                             p.get('default_database'))
    starttime = time.time()
    export_samples_as_table(mongodb, args.project_name, {}, args.filename)
    mongodb.close()
    print 'Done in %s seconds' % int((time.time() - starttime))
