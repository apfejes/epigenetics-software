'''
Created on 2013-03-12
Takes directory of where .txt files are, extracts project information and
gets the beta values, expression values and design information.
@author: jyeung
'''

import os
import glob
import re
import CreatePanel


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
        self.betas_fname = glob.glob("*_betas.txt")
        self.design_fname = glob.glob("*_pData.txt")
        self.expressions_fname = glob.glob("*_expression.txt")
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
        self.betas = CreatePanel.CreatePanel(self.projects, 'betas', 20)
        self.design = CreatePanel.CreatePanel(self.projects, 'design')
        self.expressions = CreatePanel.CreatePanel(self.projects, 'expressions', 20)
        
        
        
