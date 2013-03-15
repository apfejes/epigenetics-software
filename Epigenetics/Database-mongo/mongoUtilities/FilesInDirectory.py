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


class Files(object):
    '''
    A list of files in a directory
    '''


    def __init__(self, Directory):
        '''
        Initialize
        '''
        self.directory = Directory
        os.chdir(Directory)
        # First, get betas, design and expression filenames
        # Second, sort them in alphabetical order
        # Third, get project name
        # 1. 
        self.betas_fname = glob.glob('*_betas.txt')
        self.design_fname = glob.glob('*_pData.txt')
        self.expressions_fname = glob.glob('*_expression.txt')
        # 2. 
        self.betas_fname.sort()
        self.design_fname.sort()
        self.expressions_fname.sort()
        # 3. 
        projects = []
        for file in self.betas_fname: 
            project_name = re.sub('\_betas.txt$', '', file)
            projects.append(project_name)
        self.projects = projects
        self.projects.sort()
        print(str(len(projects)) + ' projects found in ' + Directory)
    
    def GetBetas(self, project_name, nrows=None):
        filename = project_name + '_betas.txt'
        return pandas.read_csv(filename, sep="\t", nrows=nrows)
    
    def GetExpressions(self, project_name, nrows=None):
        filename = project_name + '_expression.txt'
        return pandas.read_csv(filename, sep="\t", nrows=nrows)
    
    def GetDesign(self, project_name, nrows=None):
        filename = project_name + '_pData.txt'
        return pandas.read_csv(filename, sep="\t", nrows=nrows)
  
    def GetAnnotation(self, nrows=None):
        return pandas.read_csv('annotation_probes.txt', sep='\t', nrows=nrows)
            


        

        
        
        
        
