'''
Created on 2013-03-12
Takes directory of where .txt files are, extracts project information and
gets the beta values, expression values and design information.
@author: jyeung
'''

import os
import glob
import re
import pandas
import pymongo
from pymongo import MongoClient
import csv


class Files(object):
    '''
    A list of files in a directory
    '''


    def __init__(self, Directory):
        '''
        Initialize by gettin filenames and projectnames and sorting them.
        '''
        self.directory = Directory
        os.chdir(Directory)
        '''
        # First, get betas, design and expression filenames
        # Second, sort them in alphabetical order
        # Third, get project name
        '''
        # 1. 
        self.betas_fnames = glob.glob('*_betas.txt')
        self.design_fnames = glob.glob('*_pData.txt')
        self.expressions_fnames = glob.glob('*_expression.txt')
        self.annotation_fnames = glob.glob('*_fData.txt')
        # 2. 
        self.betas_fnames.sort()
        self.design_fnames.sort()
        self.expressions_fnames.sort()
        self.annotation_fnames.sort()
        # 3. 
        projects = []
        for file in self.betas_fnames: 
            project_name = re.sub('\_betas.txt$', '', file)
            projects.append(project_name)
        self.projects = projects
        self.projects.sort()
        print(str(len(projects)) + ' projects found in ' + Directory)
        
    def InsertRowsToDB(self, file_name, collection, **optkeys):
        '''
        Inserts entire row of a tab-delimited file into mongo. 
        The tab-delimited file should have column names (header)
        
        Inputs:
                file_name: filename of tab-delimited file. 
                collection: collection in which documents will be inserted.
                optkeys: additional key:value pairs (entered as key='value')
                        that you want to include in the document for insertion.
        
        Output:
                nrows of documents inserted into collection.
        '''
        for file in file_name:  # Since file_name is a list, we loop. 
            fname = '{0}{1}{2}'.format(self.directory, "/", file)
            print('{0}{1}'.format('Reading from ', fname))
            with open('{0}{1}{2}'.format(self.directory, "/", file), 'rb') as Data:
                reader = csv.DictReader(Data, delimiter='\t')
                print('{0}{1}'.format('Inserting rows into ', collection.name))
                for row in reader:
                    if None in row:
                        del row[None]   # Cannot insert entries with keys as None
                    '''
                    optkeys are key:value pairs that will be included into doc.
                    '''
                    for key, value in optkeys.iteritems():
                        row[key] = value
                    collection.insert(row)
        print('{0}{1}{2}'.format('There are ', 
                                 str(collection.count()), 
                                     ' docs in collection'))
    
    def InsertElementsToDB(self, file_name, collection, colname='col_name', 
                           rowname='row_name', keyname='element_name', **optkeys):
        '''
        Inserts elements of a tab-delimited file into mongo. 
        The tab-delimited file should have column names and row names. 
        
        Inputs:
                file_name: filename of tab-delimited file. 
                collection: collection in which documents will be inserted.
                colname (e.g. 'sample_name'): generic descriptor for 
                    column name. Will be used as name for key.
                rowname (e.g. 'probe_name'): generic descriptor for
                    row name. Will be used as name for key. 
                keyname (e.g. 'beta_value', 'expression_value'): key name 
                    for each key-value pair in the tab-delimited file. 
                    If tab-delimited file is a table of beta values, 
                    key should be something like 'beta_values'.
                optkeys: additional key:value pairs (entered as key='value')
                        that you want to include in the document for insertion.
        
        Output:
                nrows of documents inserted into collection.
        '''
        for file in file_name:  # file_name is a list.
            with open('{0}{1}{2}'.format(self.directory, "/", file), 'rb') as Data:
                reader = csv.reader(Data, delimiter='\t')
                headers = reader.next()
                print('{0}{1}'.format('Inserting elements into ', collection.name))
                for row in reader:
                    row_name = row[0]    # Separate row names from list
                    del row[0]    # Want a list of only values, no row names
                    for i in range(len(row)):
                        document = {}    # Empty dictionary
                        document[colname] = headers[i]
                        document[rowname] = row_name
                        document[keyname] = float(row[i])
                        for key, value in optkeys.iteritems():
                            document[key] = value
                        collection.insert(document)
                    '''
                    for header in headers:
                        for element in row:
                            document = {}    # Empty dictionary
                            document[colname] = header
                            document[rowname] = row_name
                            document[keyname] = float(element)
                            for key, value in optkeys.iteritems():
                                document[key] = value
                            collection.insert(document)
                            elementcount += 1
                    
                    rowcount += 1
                    if rowcount%100 == 0:
                        print(rowcount)
                        print(elementcount)
                    '''
        print('{0}{1}{2}'.format('There are ', 
                                 str(collection.count()), 
                                     ' docs in collection'))

                            
        
    def GetBetas(self, project_name, nrows=None):
        filename = project_name + '_betas.txt'
        return pandas.read_csv(filename, sep="\t", nrows=nrows)
    
    def GetExpressions(self, project_name, nrows=None):
        filename = project_name + '_expression.txt'
        return pandas.read_csv(filename, sep="\t", nrows=nrows)
    
    def GetDesign(self, project_name, nrows=None):
        filename = project_name + '_pData.txt'
        return pandas.read_csv(filename, sep="\t", nrows=nrows)
    
        
'''  
    def GetAnnotation(self, nrows=None):
        return pandas.read_csv('annotation_probes.txt', sep='\t', nrows=nrows)
'''            


        

        
        
        
        
