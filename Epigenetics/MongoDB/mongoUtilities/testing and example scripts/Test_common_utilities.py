'''
Created on 2013-04-15

@author: afejes
'''
import unittest

from mongoUtilities import Mongo_Connector
from MongoDB.mongoUtilities import common_utilities

class Test(unittest.TestCase):


    def test_get_chip_seq(self):
        db_name = "human_epigenetics"
        mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, db_name)
        util = common_utilities.MongoUtilities(mongo)
        results = util.get_chip_seq_sample_names()
        print results
        mongo.close()
        self.assertIsNotNone(results, "No results returned from test_get_chip_seq_samples")



if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.test_get_chip_seq']
    unittest.main()
