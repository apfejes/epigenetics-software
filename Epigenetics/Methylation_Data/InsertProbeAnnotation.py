'''
Created on 2013-04-12

@author: jyeung
'''


import csv
import sys
import os
import time

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector


# filename = '/home/jyeung/Documents/Outputs/Annotations/methyl450array_annotation_from_magda.txt'    # 450 array
# filename = '/home/jyeung/Documents/Outputs/Annotations/golden_gate_probe_info.txt'    # goldengate
database_name = 'human_epigenetics'
# database_name = 'jake_test'
collection_name = 'annotations'
arraytype = 'humanmethylation450_beadchip'


def Insert450kProbeAnnotation(filename, arraytype):
    '''
    This code may be specific for Magda's methyl 450k annotation file due to
    some specific colnames that is called ('TargetID' etc)
    
    There may (unfortunately) require some tweaking of this code for other 
    array types. 
    
    Uses DictReader to auto-create key:value pairs. Keys are columnnames.
    1. 
    Read each row as dictionary, checks to see if TargetID contains keywords,
    "cg", "ch", "rx" (otherwise it is likely a less useful entry). 
    2.
    Skip all rows that do not contain keywords in TargetID.
    3.
    If TargetID contains keywords, try to convert each value into an integer
    except for the case of CHR, where we want to keep it a string. 
    4.
    Add the following key-value pairs to dict: array_type and _id
    5. 
    Append dictionary to list. When count%20000 == 0, insert to mongo.
    6. 
    After iterating rows, bulk insert again because it is likely the loop
    exited before count was an exact multiple of 20000. 
    '''
    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)
    print('Current number of docs in collection: %s' %mongo.count(collection_name))
    
    nullcount = 0
    with open(filename, 'rb') as Data:
        reader = csv.DictReader(Data, delimiter='\t')
        BulkInsert = []
        count = 0
        for row in reader:
            if not ("cg" in row['TargetID'] or "ch" in row['TargetID'] or "rx" in row['TargetID']):
                nullcount += 1
                print('Skipped row with ID name: %s' %row['TargetID'])
                pass
            else:
                count += 1
                for key in row:
                    if key == 'CHR':    # We want value of 'CHR' to be string, not int.
                        row[key] = 'chr%s' %row[key]
                    else:
                        try:
                            row[key] = int(row[key])
                        except ValueError:    # For non-integers
                            pass
                        except TypeError:    # For NoneType
                            pass
                row['array_type'] = arraytype
                row['_id'] = '{0}{1}{2}'.format(arraytype, '_', row['TargetID'])
                BulkInsert.append(row)
                if count%20000 == 0:
                    mongo.insert(collection_name, BulkInsert)
                    BulkInsert = []
                    print('Document count in collection: %s' %mongo.count(collection_name))
        mongo.insert(collection_name, BulkInsert)
        BulkInsert = []
        print('Final doc count in collection: %s' %mongo.count(collection_name))
        print('Total number of rows skipped: %s' %nullcount)

def InsertGenericProbeAnnotation(filename, arraytype, chr_col_name, id_name):
    '''
    Inserts generic probe annotation. It will require the .txt file to have
    no messy data. 
    Inputs:
    chr_col_name:
        You require input of the chromosome column name so that it will not try
        to convert its value into an integer. 
    id_name:
        The column name of txt file that will become the _id of the mongo doc. 
        It will be concatenated with a prefix 'arraytype'.
        Choose wisely, must be unique. 
    
    '''
    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)
    print('Current number of docs in collection: %s' %mongo.count(collection_name))
    # print('{0}{1}'.format('Current number of docs in collection: ', mongo.count(collection_name)))
    
    with open(filename, 'rb') as Data:
        reader = csv.DictReader(Data, delimiter='\t')
        BulkInsert = []
        count = 0
        for row in reader:
            count += 1
            for key in row:
                if key == chr_col_name:    # We want value of 'chr_col_name' to be string, not int.
                    row[key] = 'chr%s' %row[key]
                    # pass
                else:
                    try:
                        row[key] = int(row[key])
                    except ValueError:    # If it tries to int a string...
                        pass
                    except TypeError:    # For NoneType
                        pass
            row['array_type'] = arraytype
            row['_id'] = '{0}{1}{2}'.format(arraytype, '_', row[id_name])
            BulkInsert.append(row)
            if count%20000 == 0:
                mongo.insert(collection_name, BulkInsert)
                BulkInsert = []
                print('Document count in collection: %s' %mongo.count(collection_name))
        mongo.insert(collection_name, BulkInsert)
        BulkInsert = []
        print('Final doc count in collection: %s' %mongo.count(collection_name))


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Filename and arraytype must be given on the command line.')
        sys.exit()
    filename = sys.argv[1]
    starttime = time.time()
    
    print('Using file: %s' %filename)
    
    check_450k = raw_input('Are you inserting illumina 450k methylation data? (y/n): ')
    
    if check_450k == 'y' or check_450k == 'Y':
        print('Using arraytype: %s for id prefix' %arraytype)
        Insert450kProbeAnnotation(filename, arraytype)
        
    if check_450k == 'n' or check_450k == 'N':
        print('Assuming generic annotation file, no messy entries like missing rows...')
        chr_col_name = raw_input('What is the column name of your chromosome values in the .txt file? (exact match): ')
        # chr_colname = 'Chromosome'    # For goldengate
        arraytype = raw_input('What do you want the id prefix to be? (tip: use arraytype such as golden_gate): ')
        # arraytype = 'goldengate_array'    # For goldengate
        id_name = raw_input('What do you want id suffix to be? (tip: use column name of probe identifier in .txt file): ')
        # id_name = 'cg_no'    # For goldengate
        InsertGenericProbeAnnotation(filename, arraytype, chr_col_name, id_name)
        
    print('Completed in %i seconds' %(time.time()-starttime))
