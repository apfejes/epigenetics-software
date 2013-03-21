'''
Created on 2013-03-12
mongoDB API
@author: jyeung
'''


import pymongo
from pymongo import MongoClient
import os
import glob
import csv
import gridfs
from mongoUtilities import ConnectToMongo, FilesInDirectory, InsertToMongo


'''
First, connect to db database.
Second, grab files from directory and sort them into projects.
Third, create a collection (have to type db.collection_name).
Fourth, iterate through projects to insert betas, expressions, design & annotation
'''
# 1. 
db = ConnectToMongo.ConnectToMongo()
# 2.
InputDir = '/home/jyeung/Documents/Outputs'
files = FilesInDirectory.Files(InputDir)
projects = files.projects
# 3.
collection_name = raw_input('Insert collection name: ')
collection = db[collection_name]
# collection = db.down
# 4.
for project in projects:
    
    # Get Betas
    print project
    betas = files.GetBetas(project)
    InsertToMongo.InsertBetas(betas, collection)
    del betas
    
    # Get Expression
    expressions = files.GetExpressions(project)
    InsertToMongo.InsertExpressions(expressions, collection)
    del expressions
    
    # Get Design
    design = files.GetDesign(project)
    InsertToMongo.InsertDesign(design, collection)
    del design

# Get Annotation
annotation = files.GetAnnotation()
collection = db.annotation
InsertToMongo.InsertAnnotation(annotation, collection)
del annotation


