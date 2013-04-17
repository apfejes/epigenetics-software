'''
Created on 2013-04-08

@author: jyeung
'''

import numpy as np


def CreateListFromCursor(sorted_cursor):
    '''
    Create an array with samples on the column, sample data on the row. 
    Input:
    cursor: cursor that can be iterated over
    keyname: key name from which to retrieve a value. 
    Output:
    An array containing values corresponding to the keyname. 
    '''
    doc_list = []
    for doc in sorted_cursor:
        doc_list.append(doc)
    return(doc_list)

def CreateArrayFromCursor(sorted_cursor, ncolumns, nrows, keyname):
    '''
    Create an array with samples on the column, sample data on the row. 
    Input:
    sorted_cursor: cursor that is sorted by sample names 
                   can be sorted by collection.find().sort(sample_names)
    ncolumns: number of columns in final array
    nrows: number of rows in final array
    keyname: key name from which to retrieve a value. 
    Output:
    An array containing values corresponding to the keyname. 
    '''
    doc_list = []
    for doc in sorted_cursor:
        doc_list.append(doc[keyname])
    array_data = np.array(doc_list)
    array_data = array_data.reshape(ncolumns, nrows)
    array_data = array_data.transpose()
    return(array_data)
