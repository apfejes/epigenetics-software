'''
Created on 2013-03-15

@author: jyeung
'''


import pymongo
from pymongo import MongoClient

@staticmethod
def ConnectToMongo():
    '''
    Connects and checks connection to mongoDB
    '''
    connection = MongoClient('kruncher.cmmt.ubc.ca', 27017)
    db = connection.epigenetics_database
    print('Connected to ' + db.name + '.')
    return db


