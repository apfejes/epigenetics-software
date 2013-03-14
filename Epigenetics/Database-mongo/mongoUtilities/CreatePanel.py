'''
Created on 2013-03-12
Takes a project name and extract betas, expression and design values from .txt
@author: jyeung
'''


import pandas
from pandas import*


def CreatePanel(project_names, data_type, nrows=None):
# Takes a list of x filenames and creates a panel containing x dataframes.
# 
# Inputs: 
# files: a list of x filenames containing beta-values or design-information.
#
# Outputs:
# panel: a panel containing x dataframes
    df = {}  # Empty dataframe
    for name in project_names:
        if data_type == 'betas':
            filename = name + '_betas.txt'
        elif data_type == 'expressions':
            filename = name + '_expression.txt'
        elif data_type == 'design':
            filename = name + '_pData.txt'
        else:
            raise Error("data_type must be 'betas', 'expressions', or 'design'")
        df[name] = pandas.read_csv(filename, sep="\t", nrows=nrows)
    panel = Panel(df)
    return(panel)