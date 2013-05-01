'''
Created on 2013-04-12

@author: jyeung
'''


import csv


class Samples(object):
    '''
    A class of objects representing sample information
    '''


    def __init__(self, filename):
        '''
        Constructor
        '''
        self.filename = filename
        
    def sampledict(self, samp_columns, patient_columns, project_name, sample_label_identifier):
        '''
        Creates a dictionary where index from index_sampleinfo are read
        as key:value pairs, everything else is read as a ONE key:value(list) pair
        where key=patientkey, value is rest. 
        '''
        with open(self.filename, 'rb') as SampleData:
            reader = csv.DictReader(SampleData, 
                                    delimiter='\t')
            mongoBulkInsert = []
            for DictRow in reader:
                mongoDict = {}
                patientDict = {}
                for key, value in DictRow.iteritems():
                    if key in samp_columns:
                        mongoDict[key] = value
                    elif key in patient_columns:
                        patientDict[key] = value
                    if key == sample_label_identifier:
                        mongoDict['sample_label'] = value
                    else:
                        pass
                mongoDict['patient'] = patientDict
                mongoDict['project'] = project_name
                mongoBulkInsert.append(mongoDict)
        return mongoBulkInsert
                
            
                
                
        
        