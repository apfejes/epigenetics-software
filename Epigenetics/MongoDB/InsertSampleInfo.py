'''
Created on 2013-04-12

@author: jyeung
'''


from mongoUtilities import Mongo_Connector, Samples
import csv


database_name = 'human_epigenetics'
collection_name = 'samples'

mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)

filename = '/home/jyeung/Documents/Outputs/Down/down_pData.txt'

sample_info = Samples.Samples(filename)

columns_sample = ['SampleID', 'SampleLabel', 'Sample Group', 'Current_Age', 'Test_Date',
                   'Sample Section', 'Sample_Well', 'Sentrix Barcode']
columns_patient = ['Total_BriefPraxis', 'DRM_SumofSocial', 'Handedness', 'Sex', 
                   'Level_of_Intellectual_Delay', 'DMR_SumofCognitive', 
                   'Percentage_BriefPraxis']

bulkInsert = sample_info.sampledict(columns_sample, columns_patient)
sampid = mongo.insert(collection_name, bulkInsert)







