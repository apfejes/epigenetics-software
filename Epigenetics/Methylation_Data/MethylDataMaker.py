'''
Created on 2013-04-09

@author: jyeung
'''


# from mongoUtilities import FilesInDirectory
from MongoDB.mongoUtilities import Mongo_Connector, FilesInDirectory


database_name = 'human_epigenetics'
collection_name = 'methylation'
# Connect to database
mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)
collection = mongo.db[collection_name]
# Set directory, grab all files in that directory.
InputDir = '/home/jyeung/Documents/Outputs/Down'
files = FilesInDirectory.Files(InputDir)
Bulk = files.InsertDataToDB(collection)