'''
Created on 2013-04-17

@author: jyeung, apfejes
'''

import sys
import time
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import InsertBatch
import Mongo_Connector

def ReadRObject(mongo, rdatafile):
    '''
    Takes a methylumi object and writes beta, expression and phenoData to .txt
    
    Uses rpy2 library.
    
    Modified to accept data directly from an R object, then insert it into the 
    database via Insert Branch.  Shortcuts the export process, to make it more
    efficient
    '''

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

    row_names = robjects.r('rownames(fData(methylObj))')
    col_names = robjects.r('colnames(fData(methylObj))')
    for i, c in enumerate(col_names):
        col_names[i] = c.lower()

    AllProbes = []
    batch_size = 5000
    batch = 0
    end = -1

    while (batch) * batch_size < rows_fdata:
        time1 = time.time()
        start = end + 1
        end = (batch + 1) * batch_size
        if end > rows_fdata:
            end = rows_fdata
        t0 = time.time()
        items = [{} for k in range(start, end + 1)]    # zero to batch_size-1
        for x in range(1, cols_fdata + 1):    # one to cols_fdata  - the column number - iterate.
            column = robjects.r('fData(methylObj)[' + str(start) + ':' + str(end) + ',' + str(x) + ',drop=FALSE]')
            lev = False
            if hasattr(column.rx(1, 1), "levels"):
                lev = True
                column = robjects.r('as.character(fData(methylObj)[' + str(start) + ':' + str(end) + ',' + str(x) + '])')
            for y in range(1, (end - start + 2)):    # the data
                if lev:
                    items[y - 1][col_names[x - 1]] = column.rx(y)[0]
                else:
                    items[y - 1][col_names[x - 1]] = column.rx(y, 1)[0]
        batch += 1
        time2 = time.time()
        print "Batch %i completed at %f seconds" % (batch, time2 - time1)
        ib = mongo.InsertBatchToDB("annotations", items)

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print 'RData filename must be given as the second parameter.'
        print "eg. python GenerateAnnotationFromFData.py /directory/database.RDATA"
        sys.exit()


    db_name = "human_epigenetics"
    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, db_name)
    starttime = time.time()
    rdatafile = sys.argv[1]
    data = ReadRObject(mongo, rdatafile)
    print('Done in %s seconds') % int((time.time() - starttime))
