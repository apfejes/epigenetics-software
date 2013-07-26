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
    cols_fdata = size_fdata[1]
    print "fdata rows:", rows_fdata
    fdata_row = robjects.r('fData(methylObj)')
    # print "Type fdata:", type(fdata)

    row_names = robjects.r('rownames(fData(methylObj))')
    col_names = robjects.r('colnames(fData(methylObj))')
    for i, c in enumerate(col_names):
        col_names[i] = c.lower()
    # print "colnames:", col_names

    AllProbes = []
    batch_size = 1000
    batch = 0
    end = -1

    while (batch) * batch_size < rows_fdata:
        time1 = time.time()
        start = end + 1
        end = (batch + 1) * batch_size
        if end > rows_fdata:
            end = rows_fdata
        t0 = time.time()
        items = [{} for k in range(batch_size)]    # zero to batch_size-1
        for x in range(1, cols_fdata + 1):    # one to cols_fdata  - the column number - iterate.
            column = robjects.r('fData(methylObj)[' + str(start) + ':' + str(end) + ',' + str(x) + ',drop=FALSE]')
            lev = False
            levels = ""
            if hasattr(column.rx(1, 1), "levels"):
                lev = True
                levels = robjects.r('factor(fData(methylObj)[' + str(start) + ':' + str(end) + ',' + str(x) + '], ordered=TRUE)')
            else:
                levels = ""
            for y in range(1, batch_size + 1):    # the data
                print "x, y = %i, %i" % (x, y)
                if lev:
                    items[y - 1][col_names[x - 1]] = levels.rx(y - 1)
                else:
                    items[y - 1][col_names[x - 1]] = column.rx(y, 1)[0]
        print "Item zero", items[0]
        batch += 1
        time2 = time.time()
        print "Batch %i completed at %f seconds" % (batch, time2 - time1)
        ib = InsertBatch.InsertBatchToDB("annotations", items)
        time3 = time.time()
        print "Batch %i inserted in %f seconds" % (batch, time3 - time2)




    return AllProbes


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('RData filename must be given.')
        sys.exit()
    starttime = time.time()
    rdatafile = sys.argv[1]
    data = ReadRObject(rdatafile)

    print('Done in %s seconds') % int((time.time() - starttime))
