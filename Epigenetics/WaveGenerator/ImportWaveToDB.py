'''
Created on 2013-03-27

@author: afejes
'''
from MongoDB.mongoUtilities import Mongo_Connector
import sys


def run(file_name):
    print file_name

    mongo = Mongo_Connector.MongoConnector("waves", "wave")
    f = open(file_name, 'r')    # open file
    for line in f:
        if line.startswith("#"):
            continue
        else:
            a = line.split("\t")
            wave = {}
            wave["chromosome"] = a[0]
            wave["position"] = a[1]
            wave["stddev"] = a[2]
            wave["item"] = a[3]
            mongo.insert(wave)
    mongo.close()


    #  while not None
        # read the wave
        # insert the wave into



if __name__ == '__main__':
    file_name = sys.argv[1]
    run(file_name)

