'''
Created on 2013-03-27

@author: afejes
'''


from pymongo.mongo_client import MongoClient
import sys




def __init__(self, collection_name):
    '''wrapper around connect to Mongo, in order to consolidate all of the 
    necessary connections.'''
    try:
        self.connection = MongoClient('kruncher.cmmt.ubc.ca', 27017)
        self.db = self.connection.epigenetics_database
        print('Connected to ' + self.db.name + '.')
        self.collection = self.db[collection_name]    # Create a collection for inserting documents, user input.
    except :
        sys.exit("Failure to connect to database")

def insert(self, dictionary):
    self.collection.insert(dictionary)


