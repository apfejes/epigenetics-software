'''
Created on 2013-03-12
Takes directory of where .txt files are, extracts project information and
gets the beta values, expression values and design information.
@author: jyeung
'''


import os
import glob
import re
import csv
import sys
from time import time

class Files(object):
    '''
    A list of files in a directory
    '''


    def __init__(self, collection):
        print collection
#         '''
#         Initialize by getting filenames and projectnames and sorting them.
#         '''
#         self.directory = Directory
#         os.chdir(Directory)
#         '''
#         # First, get betas, design and expression filenames
#         # Second, sort them in alphabetical order
#         # Third, get project name
#         '''
#         # 1.
#         self.betas_fname = glob.glob('*_betas.txt')
#         self.design_fname = glob.glob('*_pData.txt')
#         self.expressions_fname = glob.glob('*_expression.txt')
#         self.annotation_fname = glob.glob('*_fData.txt')
# 
#         '''
#         Concatenate directory with beta filename
#         '''
#         self.betas_fname = '{0}{1}{2}'.format(self.directory, "/", self.betas_fname[0])
#         self.expressions_fname = '{0}{1}{2}'.format(self.directory, "/", self.expressions_fname[0])



    def InsertDataToDB(self, collection):
        '''
        ***        
        Takes beta values and expression values and inserts into mongoDB.
        The document would contain values for beta and exprs, probe_id and 
        sample id. 
        
        Used by: MethylDataMaker.py in Methylation_Data
        '''
        
        #array passed by Anthony
        data = {'c001':(0,0), 'c002':(1,2), 'c003':(4,5)}
        
        BulkInsert = []
        count = 0
        number_of_inserts = 0
        t0 = time()
        
        for probe_id, (sample_id, beta, mvalue) in data.iteritems():
            document = {}
            document['sample_id'] = sample_id
            document['probe_id'] = probe_id
            document['beta_value'] = float(beta)
            document['m_value'] = float(mvalue)
            BulkInsert.append(document)
                
            if count%100 == 0:
                number_of_inserts += len(BulkInsert)
                collection.insert(BulkInsert)
                print(('{0}{1:,}{2}{3}{4}').format('    ',len(BulkInsert),'documents inserted in',(time()-t0),' seconds.'))
                print(('{0}{1:,}').format('The number of added documents adds up to', number_of_inserts))
                t0 = time()
                
                BulkInsert = []

        print('{0}{1}{2}'.format('*** There are now ',
                                 str(collection.count()),
                                     ' docs in the collection. ***'))
        return number_of_inserts



