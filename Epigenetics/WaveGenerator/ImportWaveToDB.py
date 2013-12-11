'''
Created on 2013-03-27

@author: afejes, sbrown
'''

import sys
import os


_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
while ("WaveGenerator" in _root_dir):
    _root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _cur_dir + os.sep + "Utilities")
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
sys.path.insert(0, _root_dir + os.sep + "WaveGenerator" + os.sep + "Utilities")

import Mongo_Connector
import CommonUtils.Parameters as Parameters
import StringUtils

import argparse

def create_param_obj(param_file):
    '''copy of function in The WaveGenerator - should be refactored to remove redundancy!!'''
    if os.path.exists(param_file):
        return Parameters.parameter(param_file).parameters
    else:
        print "Could not find input parameter file"
        sys.exit()


def run(PARAM, wave_data_file, wave_input_file, test):
    '''simple script for reading in a wave file and inserting it into a table in a mongodb database.'''

    # wave_data_file = raw_input('wave file to load: ')
    while not os.path.isfile(wave_data_file):
        print "Unable to find file %s" % wave_data_file
        # wave_data_file = raw_input('wave file to load: ')
        sys.exit()
    # wave_input_file = raw_input('parameter file used to generate waves: ')
    while not os.path.isfile(wave_input_file):
        print "Unable to find file %s" % wave_input_file
        # wave_input_file = raw_input('parameter file used to generate waves: ')
        sys.exit()
    # cell_line = raw_input('Insert name of the cell line: ')
    # chip = raw_input('Name of the ChIP target : ')

    print "Patient data can be entered after this insert via UpdateWaveMetadataToDB script."
    '''
    patient_data = str.lower(raw_input("Do you have patient data to enter for this sample [y/n]:"))
    while not (patient_data == 'y' or patient_data == 'n' or patient_data == 'yes' or patient_data == 'no'):
        print "response %s not understood." % patient_data
        patient_data = str.lower(raw_input("Do you have patient data to enter for this sample [y/n]:"))

    patient_dict = {}
    if patient_data == 'y' or patient_data == 'yes':
        print "please enter key value pairs in the form key=value, enter a blank line to end input"
        while True:
            line = raw_input("")
            if len(line) == 0:
                break
            else:
                st = str.split(line, "=", 1)
                patient_dict[st[0]] = st[1]
    '''
    '''
    db_names = {0:"arabidopsis_epigenetics",
                1:"human_epigenetics",
                2:"yeast_epigenetics",
                3:"test"}
    db_choice = -1
    while not (db_choice >= 0 and db_choice < len(db_names)):
        for y in db_names:
            print "%i - %s" % (y, db_names[y])
        db_choice = int(raw_input("select a database to insert records into."))
    db_name = db_names[db_choice]
    '''
    print "Data being imported into database: ", PARAM.get("default_database")

    print "Thanks - Data has been collected."
    print "opening connection(s) to MongoDB..."
    mongo = Mongo_Connector.MongoConnector(PARAM.get("server"), PARAM.get("port"), PARAM.get("default_database"))
    # TODO: Make this work
#     mongo.ensure_index("samples", "_id")
#     mongo.ensure_index("samples", "haswaves")
#     mongo.ensure_index("samples", {("haswaves", 1), ("use", 1)})
#     mongo.ensure_index("waves", "_id")
#     mongo.ensure_index("waves", "pos")
#     mongo.ensure_index("waves", {"chr":1, "pos":1})
#     mongo.ensure_index("waves", {"chr":1, "pos":1, "sample_id":1})
#     mongo.ensure_index("waves", {"sample_id":1, "height":1})
#     mongo.ensure_index("waves", {"sample_id":1, "stddev":1})

    '''Changing to not update this information, will update later from metadata file (see directly below)
    print "processing %s..." % wave_input_file
    sample = create_param_obj(wave_input_file)
    sample['cell_line'] = cell_line
    sample['chip'] = chip
    sample['haswaves'] = True    # used to indicate a sample has wave data
    collection_name = "samples"
    sample_id = mongo.insert(collection_name, sample)
    '''
    print "processing %s..." % wave_input_file
    sample = create_param_obj(wave_input_file)
    # sample['cell_line'] = "" ##stored as strain_background in metadata update file
    # sample['chip'] = "" ##stored as antibody in metadata update file
    sample['haswaves'] = True    # used to indicate a sample has wave data
    # overwrite param file input and output names
    sample['input_file'] = StringUtils.rreplace(wave_data_file, '.waves', '.wig', 1)
    sample['output_path'] = os.path.dirname(wave_data_file) + "/"
    sample['file_name'] = os.path.basename(wave_data_file)

    if args.hide:
        sample['hide'] = True    # Default to not hiding samples. Only once metadata is added is hide set to False
    else:
        sample['hide'] = False
    if test:
        sample['sample_id'] = "00test" + os.path.basename(wave_data_file)
    else:
        sample['sample_id'] = os.path.basename(wave_data_file)
    collection_name = "samples"
    sample_id = mongo.insert(collection_name, sample)



    # test if test if record with that cell line name already exists
    # if it exists, check if information matches
        # test if which fields are different - check if user wants to update or overwrite
        # test if
    collection_name = "waves"
    print "processing %s..." % wave_data_file
    print "Before insert, collection \'%s\' contains %i records" % \
                        (collection_name, mongo.count(collection_name))
    f = open(wave_data_file, 'r')    # open file
    count = 1
    to_insert = []
    for line in f:
        if line.startswith("#"):
            continue
        else:
            a = line.split("\t")
            wave = {}
            wave["chr"] = "chr" + a[0].replace("chr", "").upper()
            wave["pos"] = int(a[1])
            wave["stddev"] = int(a[2])
            wave["height"] = float(a[3])
            wave["sample_id"] = sample_id
            to_insert.append(wave)
            # mongo.insert("waves", wave)
            if count % 10000 == 0:
                print "%i lines processed" % count
                mongo.insert("waves", to_insert)
                to_insert = []
            count += 1
    if len(to_insert) > 0:
        mongo.insert("waves", to_insert)
    f.close()
    print "Collection \'%s\' now contains %i records" % \
                        (collection_name, mongo.count(collection_name))
    mongo.close()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("wavefile", help = "Wave file (.wave) to input into the database", type = str)
    parser.add_argument("parameterfile", help = "Parameter file (.input) to input into the database", type = str)
    parser.add_argument("-hide", help = "if this flag is provided, then the hide flag is set to true, otherwise, it is set to false.", action = "store_true")
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)
    parser.add_argument("-test", help = "if this flag is provided, then the test flag is set to true (no metadata required to view in db), otherwise, it is set to false.", action = "store_true")
    args = parser.parse_args()

    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)

    run(p, args.wavefile, args.parameterfile, args.test)
    print "Completed."

