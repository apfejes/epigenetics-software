'''
Created on 2013-05-02

@author: apfejes
'''

__updated__ = "2014-01-17"

import sys
import os
import time

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
while ("Methylation_Data" in _root_dir):
    _root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")

import Parameters
import Mongo_Connector


def UpdateRecords():
    '''update records'''
    starttime = time.time()

    treatment = {"V01.01.2":"P1", "V02.01.3":"P2", "V03.01.4":"V3", "V04.01.5":"V4", "V05.02.2":"P1", "V06.02.3":"P2", "V07.02.4":"V3", "V08.02.5":"V4", "V09.03.2":"V1", "V10.03.3":"V2", "V11.03.4":"P3", "V12.03.5":"P4", "V13.04.2":"V1", "V14.04.3":"V2", "V15.04.4":"P3", "V16.04.5":"P4", "V17.05.2":"V1", "V18.05.3":"V2", "V19.05.4":"P3", "V20.05.5":"P4", "V21.06.2":"V1", "V22.06.3":"V2", "V23.06.4":"P3", "V24.06.5":"P4", "V25.07.2":"P1", "V26.07.3":"P2", "V27.07.4":"V3", "V28.07.5":"V4", "V29.08.2":"P1", "V30.08.3":"P2", "V31.08.2":"P1", "V32.08.3":"P2", "V33.09.2":"V1", "V34.09.3":"V2", "V35.09.4":"P3", "V36.09.5":"P4", "V37.10.2":"P1", "V38.10.3":"P2", "V39.10.4":"V3", "V40.10.5":"V4", "V41.11.2":"V1", "V42.11.3":"V2", "V43.11.4":"P3", "V44.11.5":"P4", "V45.11.2":"V1", "V46.11.3":"V2", "V47.12.2":"P1", "V48.12.3":"P2", "V49.12.2":"P1", "V50.12.3":"P2", "V51.13.2":"V1", "V52.13.3":"V2", "V53.13.4":"P3", "V54.13.5":"P4", "V55.14.2":"V1", "V56.14.3":"V2", "V57.14.4":"P3", "V58.14.5":"P4", "V59.15.2":"P1", "V60.15.3":"P2", "V61.15.4":"V3", "V62.15.5":"V4", "V63.16.2":"P1", "V64.16.3":"P2", "V65.16.4":"V3", "V66.16.5":"V4", "V67.17.2":"P1", "V68.17.3":"P2", "V69.17.4":"V3", "V70.17.5":"V4", "V71.18.2":"P1", "V72.18.3":"P2", "V73.18.4":"V3", "V74.18.5":"V4", "V75.19.2":"V1", "V76.19.3":"V2", "V77.19.4":"P3", "V78.19.5":"P4", "V79.20.2":"V1", "V80.20.3":"V2", "V81.20.4":"P3", "V82.20.5":"P4", "V83.22.2":"V1", "V84.22.3":"V2"}

    samples = mongo.find("samples", {'project': project}, {"sampleid":1, "_id":1})    # get all samples
    count = 0
    for s in samples:
        updateDict = {}
        updateDict['sample_number'] = int(s['sampleid'][1:3])
        updateDict['participant'] = int(s['sampleid'][4:6])
        updateDict['visit'] = int(s['sampleid'][7:])
        updateDict['treatment'] = treatment[s['sampleid']]
        # print "updateDict = ", updateDict
        setDict = {'$set': updateDict}
        mongo.update("samples", {"project":project, "_id":s['_id']}, setDict)
        count += 1
    # distinct = mongo.distinct(collection_name, 'chr')
    print "%s records updated" % count
    # print distinct

    print 'Done in %i seconds' % (time.time() - starttime)



if __name__ == "__main__":
    print "code last updated on", __updated__
    p = Parameters.parameter()
    mongo = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    project = "Valproate"
    UpdateRecords()
    mongo.close()


