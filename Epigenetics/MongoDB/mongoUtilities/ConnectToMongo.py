'''
Created on 2013-03-15

@author: jyeung
'''


# import pymongo
from pymongo import MongoClient


def ConnectToMongo(database):
    '''
    Connects and checks connection to mongoDB
    '''
    connection = MongoClient('kruncher.cmmt.ubc.ca', 27017)
    db_name = database
    db = connection[database]
    print('Connected to ' + db.name + '.')
    return db


