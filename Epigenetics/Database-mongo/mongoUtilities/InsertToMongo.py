'''
Created on 2013-03-15

@author: jyeung
'''


import pymongo
from pymongo import MongoClient
import pandas


def InsertBetas(betas, collection):
    for column_index in range(0, len(betas.columns)):
        sample_name = str(betas.columns[column_index])
        for row_index in range(0, len(betas.index)):
            probe_index = betas.index[row_index]
            beta_value = betas[sample_name][row_index]
            beta_document = {'sample_name': str(sample_name),
                             'probe_index': str(probe_index),
                             'beta_value': str(beta_value)}
            collection_id = collection.insert(beta_document) 
            
def InsertExpressions(expressions, collection):
    for column_index in range(0, len(expressions.columns)):
        sample_name = str(expressions.columns[column_index])
        for row_index in range(0, len(expressions.index)):
            probe_index = expressions.index[row_index]
            expression_value = expressions[sample_name][row_index]
            expression_document = {'sample_name': str(sample_name),
                             'probe_index': str(probe_index),
                             'beta_value': str(expression_value)}
            collection_id = collection.insert(expression_document)
            
def InsertDesign(design, collection):
    for row_index in range(0, len(design.index)):
        design_document = {} # Initialize empty document
        #for column_index in range(0, len(design.columns)):
        for column_index in range(0, 4):
            design_attribute = str(design.columns[column_index])
            design_value = str(design[design_attribute][row_index])
            design_attribute = design_attribute.replace('.', '_')
            design_value = design_value.replace('.', '_')
            design_document[design_attribute] = design_value
        collection_id = collection.insert(design_document)

def InsertAnnotation(annotation, collection):
    for row_index in range(0, len(annotation.index)):
        annotation_document = {} # Initialize
        for column_index in range(0, len(annotation.columns)):
            annotation_attribute = str(annotation.columns[column_index])
            annotation_value = str(annotation[annotation_attribute][row_index])
            annotation_attribute = annotation_attribute.replace('.', '_')
            annotation_value = annotation_value.replace('.', '_')
            annotation_document[annotation_attribute] = annotation_value
        # print(annotation_document)
        collection_id = collection.insert(annotation_document)