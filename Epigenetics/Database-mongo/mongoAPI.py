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
from mongoUtilities import FilesInDirectory


connection = MongoClient('kruncher.cmmt.ubc.ca', 27017)
db = connection.epigenetics_database
# Add code to test connection
OutputDir = "/home/jyeung/Documents/Outputs"
files = FilesInDirectory.Files(OutputDir)
i = 0 # Project index, i
j = 0 # column index, j
df = files.expressions[files.projects[i]]
column_one = df.columns[j]
expression_probe_1 = {"project_name": str(files.projects[i]), 
                      "sample_name": df.columns[j], 
                      "probe_index": str(df.index[i]), 
                      "beta_value" : column_one[0]} 
new_collection = db.new_collection
new_collection_id = new_collection.insert(expression_probe_1)






