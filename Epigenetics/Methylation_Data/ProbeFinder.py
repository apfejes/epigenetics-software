'''
Created on 2013-04-10

@author: jyeung
'''


from MongoDB.mongoUtilities import Mongo_Connector
from annotUtilities import ChrLocPairs


annot_database = 'annotation'
annot_collection = 'methylation'
probe_database = 'data'
probe_collection = 'methyl450k15'

mongo_annot = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, annot_database)
mongo_data = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, probe_database)

pair1 = (17, 41245000)    # Chromosomme, location of BRCA1
pair2 = (1, 149859050)    # HISTH2A2
pair3 = (17, 7844000)    # CNTROB

pairs = ChrLocPairs.ChrLocPairs(pair1, pair2, pair3)

print pairs.dic





'''
pairs_total = [pair1, pair2, pair3] 


for (chromo, loc) in pairs_total:
    chrloc_dic[chromo] = loc
    list_chr.append(chromo)
    list_loc.append(loc)

print set(list_chr)
print list_loc
'''
    

'''

annot_cursor = mongo_data.find()


probes_cursor = mongo_data.find(
                    collection_name = ,
                    key='beta_value',
                    value={'$gt': 0.8},
                    sample_label=True,
                    _id=True,
                    beta_value=True)

for probe in probes_cursor:
    print probe
'''


