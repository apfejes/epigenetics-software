'''
Created on 2013-03-27

@author: afejes
'''


from pymongo.mongo_client import MongoClient
import sys


class MongoConnector():
    '''Class for simplifying the interactions with a mongodb server'''

    def __init__(self, machine, port, database_name):
        '''wrapper around connect to Mongo, in order to consolidate all of the 
        necessary connections.'''
        try:
            self.mongo = MongoClient(machine, port)
            self.db = self.mongo[database_name]    # Create a collection for inserting documents, user input.
        except Exception, e:
            print e
            sys.exit("Failure to connect to database")

    def insert(self, collection_name, dictionary):
        collection = self.db[collection_name]
        return collection.insert(dictionary)

    def count(self, collection_name):
        collection = self.db[collection_name]
        return collection.count()

    def drop(self, collection_name):
        self.db.drop_database(collection_name)
        
    def ensure_index(self, collection_name, key):
        collection = self.db[collection_name]
        return collection.ensure_index(key)
    
    def find(self, collection_name, findQuery=None, returnQuery=None):
        collection = self.db[collection_name]
        return collection.find(findQuery, returnQuery)
    
    def update(self, collection_name, queryDict, updateDict, multiOpt=True):
        collection = self.db[collection_name]
        return collection.update(queryDict, updateDict, multi=multiOpt)
        
    def close(self):
        self.db.connection.disconnect()


