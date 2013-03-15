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


db = ConnectToMongo.ConnectToMongo() # db is our database
OutputDir = '/home/jyeung/Documents/Outputs'
files = FilesInDirectory.Files(OutputDir)
projects = files.projects
# Test if there are betas, expressions and pData for each project?
for project in projects:
    print project
    betas = files.GetBetas(project)
    collection_betas = db.collection_betas
    InsertToMongo.InsertBetas(betas, collection_betas)
    del betas # Would this make it run faster??
    print('Inserted ' + str(collection_betas.count()) + ' into collection_betas.')
    expressions = files.GetExpressions(project)
    collection_expressions = db.collection_expressions
    InsertToMongo.InsertExpressions(expressions, collection_expressions)
    del expressions
    print('Inserted ' + str(collection_expressions.count()) + ' into collection_expressions.')
    design = files.GetDesign(project)
    collection_design = db.collection_design
    InsertToMongo.InsertDesign(design, collection_design)
    del design
    print('Inserted ' + str(collection_design.count()) + ' into collection_design.')
    annotation = files.GetAnnotation()
    collection_annotation = db.collection_annotation
    InsertToMongo.InsertAnnotation(annotation, collection_annotation)
    del annotation
    print('Inserted ' + str(collection_annotation.count()) + ' into collection_annotation.')
    

