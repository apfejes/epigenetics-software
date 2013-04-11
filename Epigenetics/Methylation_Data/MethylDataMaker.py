'''
Created on 2013-04-09

@author: jyeung
'''


# from mongoUtilities import FilesInDirectory
from MongoDB.mongoUtilities import ConnectToMongo, FilesInDirectory



# Connect to database
db = ConnectToMongo.ConnectToMongo('data')
collection = db['methyl450k15']
# Set directory, grab all files in that directory.
InputDir = '/home/jyeung/Documents/Outputs/Down'
files = FilesInDirectory.Files(InputDir)

files.InsertDataToDB(collection)



            
            
            
    