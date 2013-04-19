'''
Created on 2013-04-12

@author: jyeung
'''


from mongoUtilities import Mongo_Connector, Samples
import sys


database_name = 'human_epigenetics'
collection_name = 'samples'
# filename = '/home/jyeung/Documents/Outputs/Down/down_pData.txt'
columns_sample = ['SampleID', 'SampleLabel', 'Sample Group', 'Current_Age', 'Test_Date',
                   'Sample Section', 'Sample_Well', 'Sentrix Barcode']
columns_patient = ['Total_BriefPraxis', 'DRM_SumofSocial', 'Handedness', 'Sex', 
                   'Level_of_Intellectual_Delay', 'DMR_SumofCognitive', 
                   'Percentage_BriefPraxis']
project_name = 'down'


def InsertSampleInfo(filename):
    mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)
    sample_info = Samples.Samples(filename)
    bulkInsert = sample_info.sampledict(columns_sample, columns_patient, project_name)
    sampid = mongo.insert(collection_name, bulkInsert)
    return sampid
    
    
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Filename must be given on the command line.')
        sys.exit()
    filename = sys.argv[1]
    InsertSampleInfo(filename)


    







