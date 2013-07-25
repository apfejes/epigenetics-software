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
    print('Workspace creation completed in %s seconds') % int((time.time() - starttime))

    size_fdata = robjects.r('dim(fData(methylObj))')
    print "Size fdata:", size_fdata
    fdata_row = robjects.r('fData(methylObj)')
    # print "Type fdata:", type(fdata)

    row_names = robjects.r('rownames(fData(methylObj))')
    col_names = robjects.r('colnames(fData(methylObj))')
    for i, c in enumerate(col_names):
        col_names[i] = c.lower()
    # print "colnames:", col_names

    AllProbes = []

    for i in range(0, 10):    # fdata_size):
        fdata_row = robjects.r('fData(methylObj)[' + str(i + 1) + ',1:57,drop=FALSE]')
        # print fdata_row
        probe = {}
        for j, item in enumerate(fdata_row):



            if hasattr(item, 'levels'):
                probe[col_names[j]] = item.levels[item[0] - 1]
            else:
                probe[col_names[j]] = item[0]
        print probe
        # AllProbes.append(probe)
    # return
    #        print "unconvert:", type(item), col_names[j], item
    #        if hasattr(item, 'levels'):
    #            print "convert:", type(item.levels[item[0] - 1]), col_names[j], item.levels[item[0] - 1]
    #        else:
    #            print "plain:", type(item[0]), col_names[j], item[0]

    # for j, c in enumerate(col_names):
    #        row = fdata[i]
    #        print row
    #        probe[c] = row[j]
            # fdata[i, j]
    #    print probe



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
