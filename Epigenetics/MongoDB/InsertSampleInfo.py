'''
Created on 2013-04-12

@author: jyeung
'''


from mongoUtilities import Mongo_Connector, Samples
import sys


# database_name = 'human_epigenetics'
database_name = 'jake_test'
collection_name = 'samples'
# filename = '/home/jyeung/Documents/Outputs/Down/down_pData.txt'    # Down meta file
# filename = '/home/jyeung/Documents/Outputs/Kollman_meaghan_jones/Koll.fin_pData.txt'    # Kollman meta file



# Column names for down syndrome
# columns_sample = ['SampleID', 'SampleLabel', 'Sample Group', 'Current_Age', 'Test_Date','Sample Section', 'Sample_Well', 'Sentrix Barcode']
columns_sample = ['SampleID', 'Sample Group', 'Curent_Age', 'Test_Date', 
                  'Sample_Section', 'Sample_Well', 'Sentrix Barcode']
columns_patient = ['Total_BriefPraxis', 'DRM_SumofSocial', 'Handedness', 'Sex', 
                   'Level_of_Intellectual_Delay', 'DMR_SumofCognitive', 
                   'Percentage_BriefPraxis']
project_name = 'down'

'''
# Column names for kollman
columns_sample = ['sampleID', 'stimulation', 'life_stage']
columns_patient = []
project_name = 'kollman'
'''


def InsertSampleInfo(filename, sample_label_identifier):
    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)
    sample_info = Samples.Samples(filename)
    bulkInsert = sample_info.sampledict(columns_sample, columns_patient, project_name, sample_label_identifier)
    sampid = mongo.insert(collection_name, bulkInsert)
    return sampid
    
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Filename must be given on the command line.')
        sys.exit()
    filename = sys.argv[1]
    sample_label_identifier = raw_input('Insert column name that indicates the sample label or ID: ')
    # sample_label_identifier = 'SampleID'    # for down project
    # sample_label_identifier = 'sampleID'    # for kollman project
    InsertSampleInfo(filename, sample_label_identifier)
    print('Inserted samples into db %s and collection %s' %(database_name, collection_name))


    







