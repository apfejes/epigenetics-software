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


def importObjectsSampleData(mongo, csvbeta):
    if not os.path.isfile(csvbeta):
        print "Unable to find file %s" % csvbeta
        # wave_data_file = raw_input('wave file to load: ')
        sys.exit()
    first = True
    headers = {}
    GSE = os.path.basename(csvbeta)
    GSE = GSE[0:GSE.find("_")]
    print "GSE in use: ", GSE
    count = 0
    to_insert = []
    f = open(csvbeta, 'r')    # open file
    for b_line in f:
        count += 1
        if first:
            r = b_line.split(",")
            headers = [h.replace('"', '').strip() for h in r[1:]]
            print "all headers, processed:", headers
            first = False
            continue
        # print "processing records: ", b_line
        b = b_line.split(",")
        b = [bv.replace('"', '').strip() for bv in b]
        probe_data = {}
        probe_data['pid'] = b[0]    # probe_name
        probe_data['project'] = GSE
        probe_data['b'] = {}
        b = b[1:]
        for i in range(0, len(headers)):
            if b[i] != "NA":
                probe_data['b'].update({headers[i]:float(b[i])})
        to_insert.append(probe_data)


        if len(to_insert) >= 50000:
            rows = mongo.InsertBatchToDB("methylation", to_insert)
            if rows == len(to_insert):
                print "%i rows processed - batch successfully inserted" % count
            else:
                print "%i rows processed - batch insert failed!" % count
            to_insert = []

    rows = mongo.InsertBatchToDB("methylation", to_insert)
    if rows == len(to_insert):
        print "final batch successfully inserted - %i rows processed" % count
    else:
        print "final batch insert failed! - %i rows processed" % count
    f.close()
#===============================================================================


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csvbeta", help = "The file name of the CSV beta file to import", type = str)
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)
    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)
    starttime = time.time()
    mongodb = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    importObjectsSampleData(mongodb, args.csvbeta)
    mongodb.close()
    print('Done in %s seconds') % int((time.time() - starttime))
