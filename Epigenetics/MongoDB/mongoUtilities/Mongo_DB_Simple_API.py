'''
Created on Jan 29, 2014

@author: apfejes
'''
import argparse
from CommonUtils import Parameters
from MongoDB.mongoUtilities import Mongo_Connector
import time


def export_samples_as_table(self, connector, project_name, filter):
    '''
    This routine gets you the _ids of all projects with a given set of criteria (filter), and then returns a list representing every probe position in the array for each one.
    
    '''
    filter['project'] = project_name
    # first find the samples of interest:
    cursor = connector.find("samples", filter, {"_id":1, "sampleid":1}, sortField = "sampleid")
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
    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)
    mongodb = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    starttime = time.time()
    export_samples_as_table(mongodb, args.rfile)
    mongodb.close()
    print('Done in %s seconds') % int((time.time() - starttime))