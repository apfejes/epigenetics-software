'''
Created on 2013-04-17

@author: jyeung, apfejes
'''


import sys
import time
import os
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import CommonUtils.Parameters as Parameters

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
    col_names = robjects.r('colnames(fData(methylObj))')
    for i, c in enumerate(col_names):
        col_names[i] = c.lower()

    batch_size = 5000
    batch = 0
    end = -1
    records_added_to_db = 0

    while (batch) * batch_size < rows_fdata:
        time1 = time.time()
        start = end + 1
        end = (batch + 1) * batch_size
        if end > rows_fdata:
            end = rows_fdata
        items = [{} for _k in range(start, end + 1)]    # zero to batch_size-1
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
        records_added_to_db += mongo.InsertBatchToDB("annotations", items)
    return records_added_to_db

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print 'RData filename must be given as the second parameter.'
        print "eg. python GenerateAnnotationFromFData.py /directory/database.RDATA"
        sys.exit()
    p = Parameters.parameter()
    mongo = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    starttime = time.time()
    rfile = sys.argv[1]
    ReadRObject(mongo, rfile)
    print('Done in %s seconds') % int((time.time() - starttime))
