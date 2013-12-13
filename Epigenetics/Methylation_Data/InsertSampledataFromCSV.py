'''
Created on 2013-04-17

@author: jyeung, apfejes
'''

import os
import sys
import time
import argparse
from itertools import izip

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import CommonUtils.Parameters as Parameters
# from platform import system


def importObjectsSampleData(mongo, csvbeta, csvmval):
    while not os.path.isfile(csvbeta):
        print "Unable to find file %s" % csvbeta
        # wave_data_file = raw_input('wave file to load: ')
    while not os.path.isfile(csvmval):
        print "Unable to find file %s" % csvmval

        sys.exit()
    first = True
    headers = {}
    GSE = os.path.basename(csvbeta)
    GSE = GSE[0:GSE.find("_")]
    print "GSE in use: ", GSE
    count = 0
    to_insert = []

    for b_line, m_line in izip(open(csvbeta, 'r'), open(csvmval, 'r')):    # open file
        count += 1
        if first:
            if b_line != m_line:
                print "files don't match!"
                print "header b:", b_line
                print "header m:", m_line
                sys.exit()
            else:
                print "files are matching, continuing"
            h = b_line.split(",")
            for i in range(1, len(h)):
                GSM = h[i].replace('"', '').strip()
                l = mongo.find_one("samples", {"GSE":GSE, "GSM":GSM}, {"_id":1})
                headers[i - 1] = [str(l["_id"]), GSM]
            print "all headers, processed:", headers
            first = False
            continue
        # print "processing records: ", b_line
        b = b_line.split(",")
        b = [bv.replace('"', '').strip() for bv in b]
        probe_name = b[0]
        b = b[1:]
        m = m_line.split(",")
        m = m[1:]    # discard m[0] as probe name
        m = [mv.replace('"', '').strip() for mv in m]


        for i in range(0, len(headers)):
            if b[i] != "NA":
                sample = {}
                sample["array_type"] = "humanmethylation450_beadchip"
                sample["probeid"] = probe_name    # "probeid" : "cg00000029",
                sample["sampleid"] = headers[i][0]
                sample["beta"] = float(b[i])
                sample["mval"] = float(m[i])
                # print "sample = ", sample
                to_insert.append(sample)
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


#     f.close()
#===============================================================================


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csvbeta", help = "The file name of the CSV beta file to import", type = str)
    parser.add_argument("csvmval", help = "The file name of the CSV m-val file to import", type = str)
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)
    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)
    starttime = time.time()
    mongodb = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    importObjectsSampleData(mongodb, args.csvbeta, args.csvmval)
    mongodb.close()
    print('Done in %s seconds') % int((time.time() - starttime))
