'''
Created on 2013-04-09

@author: jyeung
'''


from MongoDB.mongoUtilities import Mongo_Connector
from annotUtilities import MethylAnnotation, ListVector


database_name = 'annotation'
collection_name = 'name_chr_loc'
mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database_name)


annot = MethylAnnotation.Annotation()
list_chrloc = ListVector.ListVector(annot.GetProbeAnnot('IlluminaHumanMethylation450kCHRLOC'))
probe_names = list_chrloc.names()

for i in xrange(1, len(probe_names)+1):
    annot_dic = {}
    annot_dic['probe_name'] = probe_names.rx(i)[0]
    # start_loc may be mapped in multiple locations, take first element.
    annot_dic['start_loc'] = list_chrloc.list.rx2(i).rx2(1)[0]
    annot_dic['chromosome'] = list_chrloc.subname(i)[0]
    print annot_dic
    mongo.insert(collection_name, annot_dic)


    

