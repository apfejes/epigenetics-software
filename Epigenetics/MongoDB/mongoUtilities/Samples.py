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
        
    def nrows(self):
        '''
        Counts number of non-header rows in file. 
        It assumes you have a header, so it will really return
        total rows minus one (because one header)
        '''
        with open(self.filename, 'rb') as SampleData:
            for i, r in enumerate(SampleData):
                pass
        self.nrows = i
        return self.nrows
    
    def colnames(self):
        with open(self.filename, 'rb') as SampleData:
            reader = csv.DictReader(SampleData, delimiter='\t')
            header = reader.fieldnames
        self.colnames = header
        return self.colnames
        
    def sampledict(self, samp_columns, patient_columns):
        '''
        Creates a dictionary where index from index_sampleinfo are read
        as key:value pairs, everything else is read as a ONE key:value(list) pair
        where key=patientkey, value is rest. 
        '''
        with open(self.filename, 'rb') as SampleData:
            reader = csv.DictReader(SampleData, 
                                    delimiter='\t')
            reader.next()    # Skip header
            mongoBulkInsert = []
            for DictRow in reader:
                mongoDict = {}
                patientDict = {}
                for key, value in DictRow.iteritems():
                    if key in samp_columns:
                        mongoDict[key] = value
                    elif key in patient_columns:
                        patientDict[key] = value
                    else:
                        pass
                mongoDict['patient'] = patientDict
                mongoBulkInsert.append(mongoDict)
        return mongoBulkInsert
                
            
                
                
        
        