# Jake Yeung
# 5 March 2013
# read_probesets.py
# Takes probesets from expression data and associate probes to probesets
###############################################################################
###############################################################################


from pandas import *
import pandas # Or try import as pd if something weird happens?
import os
import glob
import operator
import random


def CreatePanel(files):
# Takes a list of x filenames and creates a panel containing x dataframes.
# 
# Inputs: 
# files: a list of x filenames containing beta-values or design-information.
#
# Outputs:
# panel: a panel containing x dataframes
    df = {}  # Empty dataframe
    for file in files:
        name = file
        df[file] = pandas.read_csv(file, sep="\t")
        
    panel = Panel(df)
    return(panel)


os.chdir("/home/jyeung/Documents/Outputs/Subset")

# First, grab betas and design data from directory
# Second, create panel containing betas, create panel containing design,
# create dataframe containing annotations
# 1.
betas_filename = glob.glob("*_betas.txt")
design_filename = glob.glob("*_pData.txt")
annotation_filename = glob.glob("*probes.txt")

# 2.
betas_panel = CreatePanel(betas_filename)
design_panel = CreatePanel(design_filename)
annotation_table = pandas.read_csv(annotation_filename, sep="\t")