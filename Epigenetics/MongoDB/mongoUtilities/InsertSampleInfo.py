'''
Created on 2013-04-12

@author: jyeung


This Code is Deprecated - Nov 28th, 2013.


'''

from time import time
import sys
import os
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
# _root_dir = os.path.dirname(_cur_dir)
# sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _cur_dir + os.sep + "mongoUtilities")
import Mongo_Connector
import Samples

_root_dir = os.path.dirname(_cur_dir)
while ("CommonUtils" in _root_dir):
    _root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import CommonUtils.Parameters as Parameters


# database_name = 'human_epigenetics'
# database_name = 'jake_test'
collection_name = 'samples'
# filename = '/home/jyeung/Documents/Outputs/Down/down_pData.txt'    # Down meta file
# filename = '/home/jyeung/Documents/Outputs/Kollman_meaghan_jones/Koll.fin_pData.txt'    # Kollman meta file


def InsertSampleInfo(param, filename, sample_label_identifier):

    mongo = Mongo_Connector.MongoConnector(param.get('server'), param.get('port'), param.get('default_database'))
    sample_info = Samples.Samples(filename)
    bulkInsert = sample_info.sampledict(columns_sample, columns_patient, project_name, sample_label_identifier)
    sampid = mongo.insert(collection_name, bulkInsert)
    return sampid


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Filename must be given on the command line.')
        sys.exit()
    filename = sys.argv[1]

    project_name = raw_input('Enter the name of the project: ')
    columns_sample = []
    columns_patient = []

    p = Parameters.parameter()

    if project_name == 'kollman':
        # Column names for kollman.
        columns_sample.extend(['sampleID', 'stimulation', 'life_stage'])

    elif project_name == 'down':
        # Column names for down syndrome.
        columns_sample.extend(['SampleID', 'Sample Group', 'Curent_Age', 'Test_Date',
                          'Sample_Section', 'Sample_Well', 'Sentrix Barcode'])
        columns_patient.extend(['Total_BriefPraxis', 'DRM_SumofSocial', 'Handedness', 'Sex',
                           'Level_of_Intellectual_Delay', 'DMR_SumofCognitive',
                           'Percentage_BriefPraxis'])
    else:
        print('\nPlease use the command \'$head ****_pData.txt\' to ' +
              'view the columns of the tabular data.')
        print('You are now being asked which are the names of ' +
              'the columns which pertain to sample information and ' +
              'which pertain to patient information.')
        while True:
            value = raw_input('\nEnter a column name that contains sample information: ')
            if value:
                print(str(len(columns_sample)) + ' names appended to list')
                entering = False
            elif value not in columns_sample:
                columns_sample.append(value)
                print('Input appended. Simply enter to terminate the list.')
        print(str(len(columns_sample)) + ' names appended to list')

        while True:
            value = raw_input('\nEnter a column name that contains sample information: ')
            if value:
                print(str(len(columns_patient)) + ' names appended to list')
                entering = False
            elif value not in columns_patient:
                columns_patient.append(value)
                print('Input appended. Simply enter to terminate the list.')
        print(str(len(columns_patient)) + ' names appended to list')

    sample_label_identifier = raw_input('\nInsert column name that indicates the sample label or ID: ')
    # sample_label_identifier = 'SampleID'    # for down project
    # sample_label_identifier = 'sampleID'    # for kollman project
    # sample_label_identifier = 'sampleID'    # for gecko project
    print('\nProject:' + project_name)
    print 'Sample Info columns: ', columns_sample
    print 'Patient Info columns: ', columns_patient
    run = ''
    while run != 'yes' and run != 'no':
        run = raw_input('\nInsert sample information into database? Please enter \'yes\' or \'no\' :')

    if run == 'yes':
        t0 = time()
        print('\nInserting samples into db %s and collection %s...' % (p.get("default_database"), collection_name))
        InsertSampleInfo(p, filename, sample_label_identifier)
        duration = time() - t0
        # if int(duration) > 1:
        #    print "Done in ", duration, " seconds."
        print('Done.')
    elif run == 'no':
        print('Not inserting sample data into database. Exiting...')
        sys.exit()









