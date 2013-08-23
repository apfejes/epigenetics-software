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

def is_int(s):
    try:
        int(s)
        return True
    except ValueError:
        return False


def ReadRObject(mongo, rdatafile, proj_name, collection_name):
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
    # Initialize the R environment
    importr('methylumi')
    print "\n rdata:", rdatafile
    robjects.r('workspace <- load(\"' + rdatafile + '\")')
    robjects.r('methylObj <- get(workspace)')

    size_pdata = robjects.r('dim(pData(methylObj))')
    size_exprs = robjects.r('dim(exprs(methylObj))')
    # size_betas = robjects.r('dim(betas(methylObj))')

    # col_name_exprs = robjects.r('rownames(exprs(methylObj))')
    # col_name_betas = robjects.r('rownames(betas(methylObj))')

    # print "Column names for exprs: %s " % (col_name_exprs)
    # print "Column names for betas: %s " % (col_name_betas)

    num_probes = size_exprs[0]
    print "num probes:", num_probes
    num_samples = size_pdata[0]
    print "num samples:", num_samples
    num_sample_fields = size_pdata[1]

    # probes = robjects.r('rownames(exprs(methylObj))')
    col_names = robjects.r('colnames(pData(methylObj))')
    columns = []
    for i, j in enumerate(col_names):
        if (j.find(".")):
            j = j.replace(".", "_")
        j = j.strip().lower()
        columns.append(j)


    sample_field = ""
    try:
        if columns.index("sampleid"):
            pass
    except ValueError:
        print "the following columns are available.  Please pick which one you'd like to use as the sample id"
        for i, j in enumerate(columns):
            print "%i, %s" % (i, j)
        sid_field = -1
        while (sid_field < 0 or sid_field >= len(columns)):
            sid_field = raw_input('Enter the number of the field to use:')
            if is_int(sid_field):
                sid_field = int(sid_field)
                if sid_field >= 0 and sid_field < len(columns):
                    sample_field = columns[sid_field]
                else:
                    sid_field = -1
            else:
                sid_field = -1


    samples = [{} for _k in range(1, num_samples + 1)]
    for count in range(1, num_sample_fields + 1):
        field = robjects.r('pData(methylObj)[,' + str(count) + ',drop=FALSE]')
        if hasattr(field.rx(1, 1), "levels"):
            field = robjects.r('as.character(pData(methylObj)[,' + str(count) + ',drop=FALSE])')
        for f in range(1, num_samples + 1):
            samples[f - 1][columns[count - 1]] = field.rx(f, 1)[0]
            samples[f - 1]["project"] = proj_name

    if sid_field != "":
        for f in range(0, num_samples):
            samples[f]["sampleid"] = samples[f][sample_field]

    sample_names = []
    for i in range(0, len(samples)):
        sample_names.append(samples[i]['sampleid'])

    mongo.InsertBatchToDB("samples", samples)    # UNCOMMENT TO SAVE TO DB.

    # get sampleIDs
    cursor = mongo.find("samples", {"sampleid": {'$in': sample_names}, "project":proj_name}, {"_id":1}, None)
    SampleIDs = []
    for record in cursor:
        SampleIDs.append(str(record["_id"]))
    # process betas and exprs

    batch_size = 5000
    batch = 0
    end = -1
    records_added_to_db = 0

#     sys.exit()

    while (batch) * batch_size < num_probes:
        time1 = time.time()
        start = end + 1
        end = (batch + 1) * batch_size
        print "start, end (%i, %i)" % (start, end)
        if end > num_probes:
            end = num_probes

        for x in range(1, num_samples + 1):    # one to number of samples  - the column number - iterate.
            items = [{} for _k in range(start, end + 1)]    # zero to batch_size-1
            betas = robjects.r('betas(methylObj)[' + str(start) + ':' + str(end) + ',' + str(x) + ',drop=FALSE]')    # don't worry about levels. Data will always be floats, for this table
            rows = robjects.r('rownames(betas(methylObj)[' + str(start) + ':' + str(end) + ',' + str(x) + ',drop=FALSE])')

            for y in range(1, (end - start + 1)):    # the data
                items[y - 1]['sampleid'] = SampleIDs[x - 1]
                items[y - 1]['array_type'] = "humanmethylation450_beadchip"
                items[y - 1]["beta"] = betas.rx(y, 1)[0]
                # print "row = ", rows.rx(y)[0]
                items[y - 1]['probeid'] = rows.rx(y)[0]
            mvals = robjects.r('exprs(methylObj)[' + str(start) + ':' + str(end) + ',' + str(x) + ',drop=FALSE]')    # don't worry about levels. Data will always be floats, for this table
            for y in range(1, (end - start + 1)):    # the data
                items[y - 1]["mval"] = mvals.rx(y, 1)[0]
            records_added_to_db += mongo.InsertBatchToDB(collection_name, items)
        batch += 1
        time2 = time.time()
        print "Batch %i completed at %f seconds" % (batch, time2 - time1)

    return records_added_to_db


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('RData filename must be given.')
        sys.exit()
    starttime = time.time()
    rdata_file = sys.argv[1]
    db_name = "human_epigenetics"
    collection = "methylation"
    project_name = raw_input('Enter the name of the project to insert in the ' + collection + ' collection of the ' + db_name + ' database: ')
    mongodb = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, db_name)
    ReadRObject(mongodb, rdata_file, project_name, collection)
    print('Done in %s seconds') % int((time.time() - starttime))
