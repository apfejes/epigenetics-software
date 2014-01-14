'''
Created on 2013-05-02

@author: jyeung
'''

import sys
import os
import time
import argparse

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import Parameters
import Mongo_Connector

def gene_to_lower():
    '''append chr prefix.'''
    starttime = time.time()
    cursor = mongodb.find('ensgenes', {}, {"name":1, "_id":0})
    for gene in cursor:
        # print "gene.name = %s" % (gene['name'])
        mongodb.update('ensgenes', {"name":gene['name']}, {'$set': {'namelc':gene['name'].lower()}})
    print 'Done in %i seconds' % (time.time() - starttime)




if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("csvbeta", help = "The file name of the CSV beta file to import", type = str)
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)
    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)
    mongodb = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    gene_to_lower()
    mongodb.close()


