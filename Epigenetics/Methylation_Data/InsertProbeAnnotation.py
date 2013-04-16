'''
Created on 2013-04-12

@author: jyeung
'''


from MongoDB.mongoUtilities import Mongo_Connector
import csv


filename = '/home/jyeung/Documents/Outputs/Down/down_fData.txt'
database_name = 'human_epigenetics'
collection_name = 'annotations'
arraytype = 'humanmethylation450_beadchip'

mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)

nullcount = 0
with open(filename, 'rb') as Data:
    reader = csv.DictReader(Data, delimiter='\t')
    BulkInsert = []
    count = 0
    for row in reader:
        if not ("cg" in row['TargetID'] or "ch" in row['TargetID'] or "rx" in row['TargetID']):
            nullcount += 1
            print('{0}{1}'.format('Skipped row with ID name: ', row['TargetID']))
            pass
        else:
            count += 1
            for key in row:
                if key == 'CHR':
                    pass
                else:
                    try:
                        row[key] = int(row[key])
                    except Exception:
                        pass
            row['array_type'] = arraytype
            row['_id'] = '{0}{1}{2}'.format(arraytype, '_', row['TargetID'])
            BulkInsert.append(row)
            if count%20000 == 0:
                mongo.insert(collection_name, BulkInsert)
                BulkInsert = []
                print('{0}{1}'.format('Document count in collection: ', mongo.count(collection_name)))
    mongo.insert(collection_name, BulkInsert)
    BulkInsert = []
    print('{0}{1}'.format('Final doc count in collection: ', mongo.count(collection_name)))
    print('{0}{1}'.format('Total number of rows skipped: ', nullcount))
