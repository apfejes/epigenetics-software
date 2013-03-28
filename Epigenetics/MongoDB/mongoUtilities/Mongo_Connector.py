'''
Created on 2013-03-27

@author: afejes
'''

from MongoDB.mongoUtilities import ConnectToMongo
from pymongo.mongo_client import MongoClient

db = None
collection = None


def Connect_to_Mongo(collection_name):
    '''wrapper around connect to Mongo, in order to consolidate all of the 
    necessary connections.'''

    try:
        connection = MongoClient('kruncher.cmmt.ubc.ca', 27017)
        db = connection.epigenetics_database
        print('Connected to ' + db.name + '.')
        db = ConnectToMongo.ConnectToMongo()
        collection = db[collection_name]    # Create a collection for inserting documents, user input.
    except :
        print("Failure to connect to database")
        return False
    return True

def insert(dictionary):
    collection.insert(dictionary)


