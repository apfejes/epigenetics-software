'''
Created on 2013-04-17

@author: jyeung, apfejes
'''

import os
import sys
import time
import argparse

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import CommonUtils.Parameters as Parameters
# from platform import system


def importObjectsSampleData(mongo, csvbeta, project_name, collection):
    if not os.path.isfile(csvbeta):
        print "Unable to find file %s" % csvbeta
        # wave_data_file = raw_input('wave file to load: ')
        sys.exit()
    first = True
    headers = {}
    count = 0
    f = open(csvbeta, 'r')    # open file
    for b_line in f:
        count += 1
        if first:
            r = b_line.split(",")
            headers = [h.replace('"', '').replace(".", "_").strip().lower() for h in r]
            print "all headers, processed:", headers
            first = False
            continue
        # print "processing records: ", b_line
        b = b_line.split(",")
        b = [bv.replace('"', '').strip() for bv in b]
        probe_data = {}
        sampleid = None
        for i, h in enumerate(headers):
            if h == 'sampleid':
                sampleid = b[i].replace(".", " ")
            elif h == 'tissue':
                probe_data['tissuetype'] = b[i]
            elif b[i]:
                probe_data[h] = b[i]

        if not sampleid:
            print "No sampleid found in this dataset. There must be a field labeled as 'sampleid'"
            sys.exit()
        # print "sid = ", sampleid
        # print "probe data = ", probe_data
        # print "Updating: ", {"project":project_name, "sampleid":sampleid}

        t = mongo.update(collection, {"project":project_name, "sampleid":sampleid}, {'$set':probe_data}, multiOpt = False)
        # print t
    f.close()
#===============================================================================


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csvmetatdata", help = "The file name of the CSV beta file to import", type = str)
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)
    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)
    starttime = time.time()
    mongodb = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    collection = "samples"
    project_name = raw_input('Enter the name of the project to insert in the ' + collection + ' collection of the ' + p.get('default_database') + ' database: ')
    importObjectsSampleData(mongodb, args.csvmetatdata, project_name, collection)
    mongodb.close()
    print('Done in %s seconds') % int((time.time() - starttime))
