'''
Created on 2013-04-17

@author: jyeung, apfejes
'''

import os
import sys
import time
import ast
import argparse

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import CommonUtils.Parameters as Parameters
# from platform import system


def importObjectsFromJSON(mongo, filename, proj, collection):
    while not os.path.isfile(filename):
        print "Unable to find file %s" % filename
        # wave_data_file = raw_input('wave file to load: ')
        sys.exit()
    f = open(filename, 'r')    # open file
    count = 1
    to_insert = []
    for line in f:
        sample = ast.literal_eval(line)
        sample['project'] = proj
        sample['tissuetype'] = sample['tissue']
        sample.pop('tissue' , None)
        to_insert.append(sample)
        # print "sample = ", sample

        if count % 10000 == 0:
            print "%i lines processed" % count
            mongo.insert(collection, to_insert)
            to_insert = []
        count += 1
    if len(to_insert) > 0:
        pass
        mongo.insert(collection, to_insert)
    f.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("jsonfile", help = "The file name of the JSON metadata file to import", type = str)
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)
    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)
    starttime = time.time()
    collection = "samples"
    project_name = raw_input('Enter the name of the project to insert in the ' + collection + ' collection of the ' + p.get('default_database') + ' database: ')
    mongo = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    importObjectsFromJSON(mongo, args.jsonfile, project_name, p.get('default_database'), collection)
    print('Done in %s seconds') % int((time.time() - starttime))
