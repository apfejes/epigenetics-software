'''
Created on 2013-03-27

@author: afejes
'''


from pymongo.mongo_client import MongoClient
import sys


class MongoConnector():



    def __init__(self, database_name, collection_name):
        '''wrapper around connect to Mongo, in order to consolidate all of the 
        necessary connections.'''
        try:
            self.mongo = MongoClient('kruncher.cmmt.ubc.ca', 27017)
            self.db = self.mongo[database_name]    # Create a collection for inserting documents, user input.
            self.collection = self.db[collection_name]
            print self.collection.name
            print self.collection.count()
            self.collection.insert({"author": "Mike"})
        except Exception, e:
            print e
            sys.exit("Failure to connect to database")

    def insert(self, dictionary):
        self.collection.insert(dictionary)


    def close(self):
        self.db.connection.disconnect()


