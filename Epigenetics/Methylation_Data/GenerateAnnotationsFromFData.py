'''
Created on 2013-04-17

@author: jyeung
'''


import sys
import time
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import InsertBatch


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
    rows_fdata = size_fdata[0]
    print "fdata rows:", rows_fdata
    fdata_row = robjects.r('fData(methylObj)')
    # print "Type fdata:", type(fdata)

    row_names = robjects.r('rownames(fData(methylObj))')
    col_names = robjects.r('colnames(fData(methylObj))')
    for i, c in enumerate(col_names):
        col_names[i] = c.lower()
    # print "colnames:", col_names

    AllProbes = []

    for i in range(0, rows_fdata):
        t0 = time.time()
        fdata_row = robjects.r('fData(methylObj)[' + str(i + 1) + ',1:57,drop=FALSE]')
        t1 = time.time()
        probe = {}
        t2 = time.time()

        for j, item in enumerate(fdata_row):
            a = 0
            try:
                a = getattr(item, 'levels')
            except AttributeError:
                probe[col_names[j]] = item[0]
            else:
                probe[col_names[j]] = a
        t3 = time.time()
        AllProbes.append(probe)
        t4 = time.time()
        print "%i => Takes %f seconds to run step 1, %f for step 2, %f for step 3"\
          % (i, (t1 - t0), (t3 - t2), (t4 - t3),)

    return AllProbes


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('RData filename must be given.')
        sys.exit()
    starttime = time.time()
    rdatafile = sys.argv[1]
    data = ReadRObject(rdatafile)
    ib = InsertBatch.InsertBatchToDB("annotations", data)
    print('Done in %s seconds') % int((time.time() - starttime))
