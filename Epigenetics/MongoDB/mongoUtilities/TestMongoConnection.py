'''
Created on 2013-03-13
Add test_collection and test_document, test that it is there, then remove
@author: jyeung
'''


import unittest
from  MongoDB.mongoUtilities import ConnectToMongo



class ConnectionTestCase(unittest.TestCase):


    def setUp(self):
        pass

    def test_add_remove(self):
        '''
        connection = MongoClient('kruncher.cmmt.ubc.ca', 27017)
        db = connection.epigenetics_database
        '''
        db = ConnectToMongo.ConnectToMongo('epigenetics_database')
        test_document = {'key 1': 'value 1',
                         'key 2': 'value 2',
                         'key 3': 'value 3'}
        test_collection = db.test_collection
        db.test_collection.drop()
        ncollections = len(db.collection_names())
        ndocuments = test_collection.count()
        # test_collection_id = db.test_collection.insert(test_document)  # don't assign to unused variable
        db.test_collection.insert(test_document)
        self.assertEqual(len(db.collection_names()), ncollections + 1,
                         "Did not create test_collection or it was already there")
        self.assertEqual(test_collection.count(), ndocuments + 1,
                         "Did not insert a document")
        db.test_collection.remove()
        self.assertEqual(test_collection.count(), 0,
                         "Did not remove all docs from test_collection")
        db.test_collection.drop()
        self.assertEqual(len(db.collection_names()), ncollections,
                         "Did not drop test_collection")



