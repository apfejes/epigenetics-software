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




    # Load .RData file
    # robjects.r('''
    #        SetupRObjectData <- function(rdatafile) {
    #            workspace <- load(rdatafile)
    #            methylObj <- get(workspace)
    #            }
    #            ''')
    # Rfunction = robjects.r['SetupRObjectData']
    # Rfunction(rdatafile)

    importr('methylumi')
    print "rdata:", rdatafile
    robjects.r('workspace <- load(\"' + rdatafile + '\")')
    robjects.r('methylObj <- get(workspace)')
    size_pdata = robjects.r('dim(pData(methylObj))')
    print "Size pdata:", size_pdata
    size_exprs = robjects.r('dim(exprs(methylObj))')
    print "Size exprs:", size_exprs
    size_betas = robjects.r('dim(betas(methylObj))')
    print "Size betas:", size_betas

    num_probes = size_exprs[0]
    print "num probes:", num_probes
    num_samples = size_exprs[1]
    print "num samples:", num_samples

    probes = robjects.r('rownames(exprs(methylObj))')
    # print "probes", probes
    for s in range(0, num_samples):    # this will be 0 to 14 for 15 samples, so will need to add one.
        beta = robjects.r('betas(methylObj)[,' + str(s + 1) + ',drop=FALSE]')
    # print "betas", beta
        exprs = robjects.r('exprs(methylObj)[,' + str(s + 1) + ',drop=FALSE]')
        print "lengths, probes %i, beta %i, exprs %i" % (len(probes), len(beta), len(exprs))
        complete = zip(probes, beta, exprs)


    # print "complete sample for ",s
    # print complete


#                write.table(exprs(methylObj),
#                            file=paste(workspace, "_expression.txt", sep=""),
#                            sep="\t", quote=FALSE, row.names=TRUE, col.names=TRUE)
#               write.table(betas(methylObj),
#                            file=paste(workspace, "_betas.txt", sep=""),
#                            sep="\t", quote=FALSE, row.names=TRUE, col.names=TRUE)


    # robjects.r('''
    #        WriteRObjectData <- function(rdatafile, outputDirectory) {
    #            setwd(outputDirectory)
    #            print(paste('Writing to: ', getwd()))
    #            workspace <- load(rdatafile)
    #            methylObj <- get(workspace)
    #            write.table(pData(methylObj),
    #                        file=paste(workspace, "_pData.txt", sep=""),
    #                        sep="\t", quote=FALSE, row.names=TRUE, col.names=TRUE)
    #            write.table(exprs(methylObj),
    #                        file=paste(workspace, "_expression.txt", sep=""),
    #                        sep="\t", quote=FALSE, row.names=TRUE, col.names=TRUE)
    #            write.table(betas(methylObj),
    #                        file=paste(workspace, "_betas.txt", sep=""),
    #                        sep="\t", quote=FALSE, row.names=TRUE, col.names=TRUE)
    #        }
    #        ''')


    # Rfunction = robjects.r['WriteRObjectData']
    # Rfunction(rdatafile, outputDirectory)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('RData filename must be given.')
        sys.exit()
    starttime = time.time()
    rdatafile = sys.argv[1]
    ReadRObject(rdatafile)
    print('Done in %s seconds') % int((time.time() - starttime))
