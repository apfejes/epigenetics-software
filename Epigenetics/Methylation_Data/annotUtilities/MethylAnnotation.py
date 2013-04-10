'''
Created on 2013-04-09

@author: jyeung
'''


import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import sys


class Annotation(object):
    '''
    A class to get various annotation information. 
    '''


    def __init__(selfparams):
        '''
        Load R library
        '''
        try:
            importr('IlluminaHumanMethylation450k.db')
            print('Loaded methyl450K R package')
        except:
            sys.exit('IlluminaHumanMethylation450k.db not installed')
            '''
            To install try running this in R or in Python (via rpy2)
            source("http://bioconductor.org/biocLite.R")
            biocLite("AnnotationForge")
            source("http://bioconductor.org/biocLite.R")
            biocLite("IlluminaHumanMethylation450k.db")
            '''
            
    def GetProbeAnnot(self, R_command):
        '''
        Gets annotation from methyl450k based on different R_commands given.
        Inputs:
                R_command: A string indicating what type of annotation to get.
                           See IlluminaHumanMethylation450k.db docuemntation
                           for complete set of commands available. 
                           
                           GetProbeAnnotation is meant to be used for 
                           commands that involve mapping information to probes.
                           
        Outputs:
                Annotation information about the probes, in a list
        '''
        pass
        # First, define some R functions which will be used.
        mapped_probesR = robjects.r['mappedkeys']
        convert2listR = robjects.r['as.list']
        getnamesR = robjects.r['names']
        unlistR = robjects.r['unlist']
        
        # Run annotation command in R
        annot_info = robjects.r[R_command]
        # Get probes related to this annotation
        mapped_probes = mapped_probesR(annot_info)
        # Convert to list
        list_annot = convert2listR(annot_info)
        # Remove any lists containing NAs
        list_annot_mapped = list_annot.rx(mapped_probes)
        return list_annot_mapped

'''
methylation_annotation = importr('IlluminaHumanMethylation450k.db')

chrloc = robjects.r['IlluminaHumanMethylation450kCHRLOC']
mapped_probesR = robjects.r['mappedkeys']
mapped_probes = mapped_probesR(chrloc)
convert2listR = robjects.r['as.list']
list_chr = convert2listR(chrloc)
list_chr_mapped = list_chr.rx(mapped_probes)

getnamesR = robjects.r['names']
probe_names = getnamesR(list_chr_mapped)

unlistR = robjects.r['unlist']
chr_unlisted = unlistR(list_chr_mapped)

probe_chr = {}
for i in xrange(1,6):
    probe_chr[probe_names[i]] = chr_unlisted[i]
'''



        