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


class Files(object):
    '''
    A list of files in a directory
    '''


    def __init__(self, Directory):
        '''
        Initialize by getting filenames and projectnames and sorting them.
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

        '''
        Concatenate directory with first beta fnames. 
        This means if you use self.betas_fnames_full, you would 
        only get one beta file, even if your directory contained several. 
        '''
        self.betas_fnames_full = '{0}{1}{2}'.format(self.directory, "/", self.betas_fnames[0])
        self.expressions_fnames_full = '{0}{1}{2}'.format(self.directory, "/", self.expressions_fnames[0])
        # 2.
        self.betas_fnames.sort()
        self.design_fnames.sort()
        self.expressions_fnames.sort()
        self.annotation_fnames.sort()
        # 3.
        projects = []
        for file_name in self.betas_fnames:
            project_name = re.sub('\_betas.txt$', '', file_name)
            projects.append(project_name)
        self.projects = projects
        self.projects.sort()
        print(str(len(projects)) + ' projects found in ' + Directory)
        

    def InsertDataToDB(self, collection, 
                        colnamebeta = 'sample_label',
                        rownamebeta = 'probe_id',
                        keynamebeta = 'beta_value',
                        keynameexprs = 'exprs_value',
                        **optkeys):
        '''
        ***This code effectively replaces the old function,
        InsertElementstoDB
        
        Takes beta values and expression values and inserts into mongoDB.
        The document would contain values for beta and exprs, probe_id and 
        sample label. 
        
        Used by: MethylDataMaker.py in Methylation_Data
        '''
        
        fbeta = open(self.betas_fnames_full)
        fexprs = open(self.expressions_fnames_full)
        
        readerbeta = csv.reader(fbeta, delimiter = '\t')
        readerexprs = csv.reader(fexprs, delimiter = '\t')
        
        headerbeta = readerbeta.next()
        headerexprs = readerexprs.next()
        if (headerbeta == headerexprs) == False:
            sys.exit('Headers of two files do not match, exiting...')
        
        BulkInsert = []
        count = 0
        number_of_inserts = 0
        while True:
            count += 1
            try:
                row_i_beta = readerbeta.next()
                row_i_exprs = readerexprs.next()
            
            except StopIteration:
                print('Stopping, no more rows to iterate.')
                break
            
                
            rowname_beta = row_i_beta[0]
            rowname_exprs = row_i_exprs[0]
            
            if (rowname_beta == rowname_exprs) == False:
                sys.exit('Rownames of two files not matching, exiting...')
            
            for i in range(0, len(row_i_beta)-1):
                document = {}
                document[colnamebeta] = headerbeta[i]
                document[rownamebeta] = rowname_beta
                document[keynamebeta] = float(row_i_beta[i+1])
                document[keynameexprs] = float(row_i_exprs[i+1])
                BulkInsert.append(document)
                
            if count%10000 == 0:
                number_of_inserts += len(BulkInsert)
                collection.insert(BulkInsert)
                print('{0}{1}{2}'.format('There are ',
                                         str(collection.count()),
                                             ' docs in collection'))
                BulkInsert = []
        number_of_inserts += len(BulkInsert)
        collection.insert(BulkInsert)
        BulkInsert = []
        fbeta.close()
        fexprs.close()
        print('{0}{1}{2}'.format('There are ',
                                 str(collection.count()),
                                     ' docs in collection'))
        return number_of_inserts



