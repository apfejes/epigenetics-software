'''
Created on 2013-04-10

@author: jyeung
'''


from MongoDB.mongoUtilities import Mongo_Connector
from annotUtilities import ChrLocPairs



annot_database = 'annotation'
# annot_collection = 'methylation'
annot_collection = 'name_chr_loc'
probe_database = 'data'
probe_collection = 'methyl450k15'

mongo_annot = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, annot_database)
mongo_data = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, probe_database)

pair1 = ("1", 53468351)
# pair2 = ("3", 37440968)
# pair3 = ("8", -87060691)
# pair4 = ("X", 68048840)
# pair5 = ("3", 171757418)

# pairs = ChrLocPairs.ChrLocPairs(pair1, pair2, pair3, pair4, pair5)
pairs = ChrLocPairs.ChrLocPairs(pair1)

curs = mongo_annot.find(annot_collection, pairs.findQuery(), pairs.returnQuery())

for doc in curs:
    print doc


'''
chrloc_cursor = mongo_annot.find(annot_collection, pairs.findQuery(), pairs.returnQuery())

list_chr = pairs.dic.keys()
# findQuery = {'chromosome': {'$in': list_chr}}
# returnQuery = {'probe_name': True}
findQuery = pairs.findQuery()
returnQuery = pairs.returnQuery()
print findQuery
print returnQuery

curs = mongo_annot.find(annot_collection, findQuery, returnQuery)

print curs.count()
'''







    





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


