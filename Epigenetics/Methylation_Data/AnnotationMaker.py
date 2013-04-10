'''
Created on 2013-04-09

@author: jyeung
'''


from MongoDB.mongoUtilities import Mongo_Connector, InsertToMongo
from annotUtilities import MethylAnnotation, ListVector


database_name = 'annotation'
collection_name = 'bioconductor_annotations'
mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)


annot = MethylAnnotation.Annotation()
list_chrloc = ListVector.ListVector(annot.GetProbeAnnot('IlluminaHumanMethylation450kCHRLOC'))
probe_names = list_chrloc.names()

annot_dic = {'location': []}    # Initialize an empty list
for i in xrange(1, len(probe_names)+1):
    annot_dic['probe_name'] = probe_names.rx(i)
    for j in xrange(1, len(list_chrloc.list.rx2(i))):
        annot_dic['location'].append(list_chrloc.list.rx2(i).rx2(j))
    mongo.insert(collection_name, annot_dic)


    

