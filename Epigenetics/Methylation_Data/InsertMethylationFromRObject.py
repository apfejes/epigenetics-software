'''
Created on 2013-04-17

@author: jyeung, apfejes
'''

import os
import sys
import time
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import argparse

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import Mongo_Connector
import CommonUtils.Types as ty
import CommonUtils.Parameters as Parameters
# from platform import system

def ReadRObject(mongo, rdatafile, proj_name, collection_name, reuse_samples):
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
    sample_row_names = robjects.r('rownames(pData(methylObj))')
    columns = []
    for i, j in enumerate(col_names):
        if (j.find(".")):
            j = j.replace(".", "_")
        j = j.strip().lower()
        columns.append(j)


    sid_field = -1
    sample_field = ""
    try:
        if columns.index("sampleid") :
            pass    # as long as an error isn't thrown, set the sample_field equal to "sampleid"
        sample_field = "sampleid"
    except ValueError:
        print "the following columns are available.  Please pick which one you'd like to use as the sample id"
        for i, j in enumerate(columns):
            print "%i, %s" % (i, j)
        while ((sid_field < 0 or sid_field >= len(columns)) and sid_field != "R"):
            sid_field = raw_input('Enter the number of the field to use, or "R" to use the rownames (eg %s, %s):'
                                  % (sample_row_names[0], sample_row_names[1]))
            if ty.is_int(sid_field):
                sid_field = int(sid_field)
                if sid_field >= 0 and sid_field < len(columns):
                    sample_field = columns[sid_field]
                else:
                    sid_field = -1
            elif sid_field == "R":
                sample_field = "R"
            else:
                sid_field = -1


    samples = [{} for _k in range(1, num_samples + 1)]
    for count in range(1, num_sample_fields + 1):
        field = robjects.r('pData(methylObj)[,%i,drop=FALSE]' % (count))
        ar = field.rx2(1)
        for f in range(1, num_samples + 1):
            samples[f - 1][columns[count - 1]] = ar[f - 1]
            samples[f - 1]["project"] = proj_name

    if sid_field == "R":
        for f in range(0, num_samples):
            samples[f]["sampleid"] = sample_row_names[f]
    elif sid_field != -1:
        for f in range(0, num_samples):
            samples[f]["sampleid"] = str(samples[f][sample_field])

    for i in range(0, len(samples)):
        samples[i]['sampleid'] = samples[i]['sampleid']    # .replace(".", "")


    sample_names = []
    for i in range(0, len(samples)):
        sample_names.append(str(samples[i]['sampleid']))

    if not reuse_samples:
        mongo.InsertBatchToDB("samples", samples)

    # get sampleIDs
    # cursor = mongo.find("samples", {"sampleid": {'$in': sample_names}, "project":proj_name}, {"_id":1}, None)
    # SampleIDs = []
    # for record in cursor:
    #    SampleIDs.append(record["_id"])

    # print "sampleids:", SampleIDs

    batch_size = 5000
    batch = 0
    end = -1
    records_added_to_db = 0

    while (batch) * batch_size < num_probes:    # process betas and exprs
        time1 = time.time()
        start = end + 1
        end = (batch + 1) * batch_size
        print "Batch %i -> (start, end) (%i, %i)" % (batch + 1, start, end)
        if end > num_probes:
            end = num_probes
        b = robjects.r('betas(methylObj)[%i:%i,,drop=FALSE]' % (start, end))
        r = robjects.r('rownames(betas(methylObj)[%i:%i,,drop=FALSE])' % (start, end))
        # m = robjects.r('exprs(methylObj)[%i:%i,,drop=FALSE]' % (start, end))    # don't worry about levels. Data will always be floats, for this table
        items = []
        for y in xrange(1, len(r) + 1):    # iterate over rows the data
            probe_data = {}
            probe_data['pid'] = r.rx(y)[0]
            probe_data['b'] = {}
            probe_data['project'] = proj_name
            for x in range(1, num_samples + 1):    # one to number of samples  - the column number - iterate.
                probe_data['b'].update({sample_names[x - 1]:b.rx(y, x)[0]})
            # print "new record = ", probe_data
            items.append(probe_data)

        records_added_to_db += mongo.InsertBatchToDB(collection_name, items)
        batch += 1
        time2 = time.time()
        print "Batch %i completed at %f seconds" % (batch, time2 - time1)

    return records_added_to_db


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("rfile", help = "R data file to import", type = str)
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)
    parser.add_argument("-reuse_samples", help = "When set, this flag prevents new sample data from being inserted, and methylation data will be connected to existing samples in the db.", action = 'store_true')

    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)
    mongodb = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    starttime = time.time()
    collection = "methylation3"
    project_name = raw_input('Enter the name of the project to insert in the ' + collection + ' collection of the ' + p.get('default_database') + ' database: ')
    ReadRObject(mongodb, args.rfile, project_name, collection, args.reuse_samples)
    mongodb.close()
    print('Done in %s seconds') % int((time.time() - starttime))
