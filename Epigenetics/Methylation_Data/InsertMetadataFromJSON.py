'''
Created on 2013-04-17

@author: jyeung, apfejes
'''

import os
import sys
import time
import ast
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
# from platform import system


def importObjectsFromJSON(mongo, filename, proj, database, collection):
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
    if len(sys.argv) < 2:
        print('RData filename must be given.')
        sys.exit()
    starttime = time.time()
    filename = sys.argv[1]
    db_name = "human_epigenetics_temp"
    collection = "samples"
    project_name = raw_input('Enter the name of the project to insert in the ' + collection + ' collection of the ' + db_name + ' database: ')
    mongodb = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, db_name)
    importObjectsFromJSON(mongodb, filename, project_name, db_name, collection)
    print('Done in %s seconds') % int((time.time() - starttime))
