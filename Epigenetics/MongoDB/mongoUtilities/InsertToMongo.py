'''
Created on 2013-03-15

@author: jyeung
'''


from pymongo import MongoClient


'''
Because sample names are the columns of the beta/expression table, 
we iterate through rows in each column.

But in design and annotation tables, the sample names are the rows, so
we iterate through columns in each row. 
'''

def InsertKeyValue(collection, **kwargs):
    document = {}    # Initialize document that is empty
    for key, value in kwargs.iteritems():
        document[key] = value
        collection.insert(document)
    print('{0}{1}{2}'.format('There are ',
                             str(collection.count()),
                                 ' docs in collection'))


'''
# The InsertBetas, Expressions, Design, Annotation functions are absolute, they are 
# now functions in FilesInDirectory class.
# 
# 

def InsertBetas(betas, collection):
    print ('Inserting betas into mongo...')
    for column_index in range(0, len(betas.columns)): # columns are samples
        sample_name = betas.columns[column_index]
        for row_index in range(0, len(betas.index)):
            probe_index = betas.index[row_index]
            beta_value = float(betas[sample_name][row_index])
            beta_document = {'sample_name': sample_name,
                             'probe_index': probe_index,
                             'beta_value': beta_value}
            # Prepared equivalent in SQL?
            collection_id = collection.insert(beta_document)
    print('Inserted ' + str(collection.count()) + ' into collection.') 
            
def InsertExpressions(expressions, collection):
    print('Inserting expressions into mongo...')
    for column_index in range(0, len(expressions.columns)): # columns = samples
        sample_name = expressions.columns[column_index]
        for row_index in range(0, len(expressions.index)):
            probe_index = expressions.index[row_index]
            expression_value = float(expressions[sample_name][row_index])
            expression_document = {'sample_name': sample_name,
                                   'probe_index': probe_index,
                                   'expression_value': expression_value}
            collection_id = collection.insert(expression_document)
    print('Inserted ' + str(collection.count()) + ' into collection.')
            
def InsertDesign(design, collection):
    print('Inserting design into mongo...')
    for row_index in range(0, len(design.index)): # rows are samples
        design_document = {} # Initialize empty document
        for column_index in range(0, len(design.columns)):
            design_attribute = str(design.columns[column_index]) # our key
            design_value = str(design[design_attribute][row_index]) # our value
            design_attribute = design_attribute.replace('.', '_') 
            # It seems mongoDB doesn't like periods as keys??
            design_document[design_attribute] = design_value # key:value pair
        collection_id = collection.insert(design_document)
    print('Inserted ' + str(collection.count()) + ' into collection.')

def InsertAnnotation(annotation, collection):
    print('Inserting annotation into mongo...')
    for row_index in range(0, len(annotation.index)): # rows are samples
        annotation_document = {} # Initialize empty document
        for column_index in range(0, len(annotation.columns)):
            annotation_attribute = str(annotation.columns[column_index]) # key
            annotation_value = annotation[annotation_attribute][row_index]
            annotation_attribute = annotation_attribute.replace('.', '_')
            # It seems mongoDB doesn't like periods in keys??
            annotation_document[annotation_attribute] = annotation_value
        collection_id = collection.insert(annotation_document)
    print('Inserted ' + str(collection.count()) + ' into collection.')
'''



