'''
Created on 2013-03-27

@author: afejes
@author: jyeung
'''


from pymongo.mongo_client import MongoClient
import sys
import types


class MongoConnector():
    '''Class for simplifying the interactions with a mongodb server'''
    BULKINSERTSIZE = 1000


    def __init__(self, machine, port, database_name):
        '''wrapper around connect to Mongo, in order to consolidate all of the 
        necessary connections.'''
        try:
            self.mongo = MongoClient(machine, port)
            self.db = self.mongo[database_name]    # Create a collection for inserting documents, user input.
        except Exception, e:    # pylint: disable=W0703
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

    def ensure_index(self, collection_name, key, background = None):
        collection = self.db[collection_name]
        if background:
            return collection.ensure_index(key, background)
        else:
            return collection.ensure_index(key)

    def drop_index(self, collection_name, index_or_name):
        collection = self.db[collection_name]
        return collection.drop_index(index_or_name)

    def find(self, collection_name, findQuery, returnQuery = None, sortField = None):
        '''sortField should be given as a dict, with the format {"field1":sortdirection}, 
        where sortdirection is a -1 or 1, depending on the direction of the sort,
        (descending, ascending, respectively)'''
        collection = self.db[collection_name]
        if sortField is None:
            return collection.find(findQuery, returnQuery)
        elif type(sortField) == types.ListType:
            return collection.find(findQuery, returnQuery).sort(sortField)
        else:
            raise Exception ("Invalid query - check sort Field type")


    def update(self, collection_name, queryDict, updateDict, multiOpt = True):
        collection = self.db[collection_name]
        return collection.update(queryDict, updateDict, multi = multiOpt)

    def remove(self, collection_name, queryDict, multiOpt = True):
        '''USE THIS FUNCTION WITH CAUTION!'''
        collection = self.db[collection_name]
        return collection.remove(queryDict, multi = multiOpt)

    def close(self):
        self.db.connection.disconnect()

    def distinct(self, collection_name, field):
        collection = self.db[collection_name]
        return collection.distinct(field)

    def InsertBatchToDB(self, collection_name, data):
        collection = self.db[collection_name]
        BulkInsert = []
        number_of_inserts = 0

        for document in data:    # for each row in array of annotations
            BulkInsert.append(document)

            if len(BulkInsert) % self.BULKINSERTSIZE == 0:
                number_of_inserts += len(BulkInsert)
                collection.insert(BulkInsert)
                BulkInsert = []

        if len(BulkInsert) > 0:
            number_of_inserts += len(BulkInsert)
            collection.insert(BulkInsert)
        return number_of_inserts

    def UpdateBatchToDB(self, collection_name, data):
        collection = self.db[collection_name]
        BulkUpdate = []
        number_of_inserts = 0

        for document in data:    # for each row in array of annotations
            BulkUpdate.append(document)

            if len(BulkUpdate) % self.BULKINSERTSIZE == 0:
                number_of_inserts += len(BulkUpdate)
                collection.update(BulkUpdate)
                BulkUpdate = []

        if len(BulkUpdate) > 0:
            number_of_inserts += len(BulkUpdate)
            collection.update(BulkUpdate)
        return number_of_inserts


