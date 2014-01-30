'''
Created on Jan 29, 2014

@author: apfejes
'''
import argparse
import time
import os
import sys

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
while ("MongoDB" in _root_dir):
    _root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
from CommonUtils import Parameters
import Mongo_Connector


def export_samples_as_table(connector, project_name, filters):
    '''
    This routine gets you the _ids of all projects with a given set of criteria (filter), and then returns a list representing every probe position in the array for each one.
    
    '''
    filters['project'] = project_name
    # first find the samples of interest:
    cursor = connector.find("samples", filters, {"_id":1, "sampleid":1}, sortField = ["sampleid"])
    ids = []
    names = {}
    for x in cursor:
        ids.append(x['_id'])
        names[x['_id']] = x['sampleid']

    # find all probe names
    target_cursor = connector.distinct("annotations", "target")

    # get the results for each probe for each sample

    print "names:", names
    for i in target_cursor:
        row = {}
        data_cursor = connector.find("methylation", {"probeid":i, "sampleid": {"$in": ids}}, {"sampleid":1, "beta":1})
        for c in data_cursor:
            row[c['sampleid']] = c['beta']
        print "row = ", row

    # wht's missing is the formatting and the sorting'


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("project_name", help = "Name of Project to Export", type = str)
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)

    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)
    mongodb = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    starttime = time.time()
    export_samples_as_table(mongodb, args.project_name, {})
    mongodb.close()
    print('Done in %s seconds') % int((time.time() - starttime))