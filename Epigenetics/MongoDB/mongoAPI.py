'''
Created on 2013-03-25

@author: jyeung
'''


# from mongoUtilities import FilesInDirectory
from MongoDB.mongoUtilities import ConnectToMongo, FilesInDirectory


# Connect to database
db = ConnectToMongo.ConnectToMongo()
# Set directory, grab all files in that directory.
InputDir = '/home/jyeung/Documents/Outputs/Down'
files = FilesInDirectory.Files(InputDir)
# Find all projects in that directory
projects = files.projects
# Create a collection for inserting documents, user input.
collection_name = raw_input('Insert collection name for inserting documents: ')
# collection_name = 'fData'
collection = db[collection_name]

'''
First, insert beta values.
Second, insert expression values.
Third, insert design values.
Fourth, insert annotation information.
'''


# 1.
files.InsertElementsToDB(files.betas_fnames,
                         collection,
                         colname = 'sample_name',
                         rowname = 'probe_name',
                         keyname = 'beta_value')
# 2.
files.InsertElementsToDB(files.expressions_fnames,
                         collection,
                         colname = 'sample_name',
                         rowname = 'probe_name',
                         keyname = 'expression_value')
# 3.
files.InsertRowsToDB(files.design_fnames, collection)

# 4.
files.InsertRowsToDB(files.annotation_fnames, collection)
