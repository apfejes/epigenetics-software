'''
Created on 2013-04-17

@author: jyeung, apfejes
'''

import os
import sys
import time
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
# from platform import system


def ReadRObject(mongo, rdatafile):
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
    print "\n rdata:", rdatafile
    robjects.r('workspace <- load(\"' + rdatafile + '\")')
    robjects.r('methylObj <- get(workspace)')

    size_pdata = robjects.r('dim(pData(methylObj))')
    size_exprs = robjects.r('dim(exprs(methylObj))')
    size_betas = robjects.r('dim(betas(methylObj))')

    col_name_exprs = robjects.r('rownames(exprs(methylObj))')
    col_name_betas = robjects.r('rownames(betas(methylObj))')

    print "Column names for exprs: %s " % (col_name_exprs)
    print "Column names for betas: %s " % (col_name_betas)

    num_probes = size_exprs[0]
    print "num probes:", num_probes
    num_samples = size_pdata[0]
    print "num samples:", num_samples
    num_sample_fields = size_pdata[1]

    probes = robjects.r('rownames(exprs(methylObj))')
    col_names = robjects.r('colnames(pData(methylObj))')
    print col_names
    samples = [{} for k in range(1, num_samples + 1)]
    for count in range(1, num_sample_fields + 1):
        field = robjects.r('pData(methylObj)[,' + str(count) + ',drop=FALSE]')
        if hasattr(field.rx(1, 1), "levels"):
            field = robjects.r('as.character(pData(methylObj)[,' + str(count) + ',drop=FALSE])')
        for f in range(1, num_samples + 1):
            samples[f - 1][col_names[count - 1]] = field.rx(f, 1)[0]
    # mongo.InsertBatchToDB("samples", samples)  #UNCOMMENT TO SAVE TO DB.
    # process betas and exprs

    batch_size = 5000
    batch = 0
    end = -1
    records_added_to_db = 0

    sys.exit()

#     while (batch) * batch_size < num_probes:
#         time1 = time.time()
#         start = end + 1
#         end = (batch + 1) * batch_size
#         if end > num_probes:
#             end = num_probes
#         items = [{} for k in range(start, end + 1)]    # zero to batch_size-1
#         for x in range(1, cols_fdata + 1):    # one to cols_fdata  - the column number - iterate.
#             column = robjects.r('fData(methylObj)[' + str(start) + ':' + str(end) + ',' + str(x) + ',drop=FALSE]')
#             lev = False
#             if hasattr(column.rx(1, 1), "levels"):
#                 lev = True
#                 column = robjects.r('as.character(fData(methylObj)[' + str(start) + ':' + str(end) + ',' + str(x) + '])')
#             for y in range(1, (end - start + 2)):    # the data
#                 if lev:
#                     items[y - 1][col_names[x - 1]] = column.rx(y)[0]
#                 else:
#                     items[y - 1][col_names[x - 1]] = column.rx(y, 1)[0]
#         batch += 1
#         time2 = time.time()
#         print "Batch %i completed at %f seconds" % (batch, time2 - time1)
#         records_added_to_db += mongo.InsertBatchToDB("annotations", items)
    return records_added_to_db



    for s in range(0, num_samples):    # this will be 0 to 14 for 15 samples, so will need to add one.

        print "Inserted Sample #", s + 1

        print "Sample %s" % (sample)



        beta = robjects.r('betas(methylObj)[,' + str(s + 1) + ',drop=FALSE]')
        print "beta %s" % (beta)
        exprs = robjects.r('exprs(methylObj)[,' + str(s + 1) + ',drop=FALSE]')
        print "exprs %s" % (exprs)


        # beta = robjects.r('betas(methylObj)[,' + str(s + 1) + ',drop=FALSE]')
        # exprs = robjects.r('exprs(methylObj)[,' + str(s + 1) + ',drop=FALSE]')
        print "lengths, probes %i, beta %i, exprs %i" % (len(probes), len(beta), len(exprs))
        complete = zip(probes, beta, exprs)
        print "complete ", complete
        print "type complete ", type(complete)

    # print "betas", beta


    # print "complete sample for ",s


    project_name = raw_input('Enter the name of the project to insert in sample table: ')



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
    db_name = "human_epigenetics"
    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, db_name)

    ReadRObject(mongo, rdatafile)



    print('Done in %s seconds') % int((time.time() - starttime))
