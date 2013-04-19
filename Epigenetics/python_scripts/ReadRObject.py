'''
Created on 2013-04-17

@author: jyeung
'''


import sys
import time
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr


def ReadRObject(rdatafile):
    '''
    Takes a methylumi object and writes beta, expression and phenoData to .txt
    
    Uses rpy2 library.
    
    robjects.r(' ') is used to talk to R. In this case, it first writes
    a function in R called 'WriteObjectData'.
    
    Second, we create a python object that can call 'WriteObjectData'
    function using robjects.r[' '].
    
    Third, we input variables from python into the python object, which allows
    the R function be run with python variables.
    '''
    # Load libraries
    importr('methylumi')
    
    # Load .RData file
    robjects.r('''
            WriteRObjectData <- function(rdatafile, outputDirectory) {
                setwd(outputDirectory)
                print(paste('Writing to: ', getwd()))
                workspace <- load(rdatafile)
                methylObj <- get(workspace)
                write.table(pData(methylObj), 
                            file=paste(workspace, "_pData.txt", sep=""), 
                            sep="\t", quote=FALSE, row.names=TRUE, col.names=TRUE)
                write.table(exprs(methylObj), 
                            file=paste(workspace, "_exprs.txt", sep=""), 
                            sep="\t", quote=FALSE, row.names=TRUE, col.names=TRUE)
                write.table(betas(methylObj), 
                            file=paste(workspace, "_betas.txt", sep=""), 
                            sep="\t", quote=FALSE, row.names=TRUE, col.names=TRUE)
            }
            ''')
    Rfunction = robjects.r['WriteRObjectData']
    Rfunction(rdatafile, outputDirectory)
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('RData filename must be given.')
        sys.exit()
    starttime = time.time()
    rdatafile = sys.argv[1]
    outputDirectory = sys.argv[2]
    ReadRObject(rdatafile)
    print('Done in %s seconds') % int((time.time()-starttime))
    