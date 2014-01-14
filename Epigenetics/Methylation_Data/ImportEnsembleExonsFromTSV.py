'''
Created on 2013-04-17

@author: jyeung, apfejes
'''

import os
import sys
import time
import argparse
import pymongo

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import CommonUtils.Parameters as Parameters
# from platform import system


def importObjectsSampleData(mongo, tsvgene):
    while not os.path.isfile(tsvgene):
        print "Unable to find file %s" % tsvgene
        sys.exit()
    headers = {}

    f = open(tsvgene, 'r')    # open file
    count = 0

    fields = {"Description":0,    # FORMERLY --
                "Ensembl Gene ID":1,    # FORMERLY 4
                "Ensembl Transcript ID":2,    # FORMERLY 5
                "Ensembl Protein ID":3,    # FORMERLY 6
                "Chromosome Name":4,    # FORMERLY 7
                "Gene Start (bp)":5,    # FORMERLY 8
                "Gene End (bp)":6,    # FORMERLY 9
                "Transcript Start (bp)":7,    # FORMERLY 10
                "Transcript End (bp)":8,    # FORMERLY 11
                "Strand":9,    # FORMERLY --
                "Associated Gene Name":10,    # FORMERLY --
                "5' UTR Start":11,    # FORMERLY 12
                "5' UTR End":12,    # FORMERLY 13
                "3' UTR Start":13,    # FORMERLY 14
                "3' UTR End":14,    # FORMERLY 15
                "CDS Length":15,    # FORMERLY 16
                "Transcript count":16,    # FORMERLY --
                "Exon Chr Start (bp)":17,    # FORMERLY 0 - BY EXON
                "Exon Chr End (bp)":18,    # FORMERLY 1 - BY EXON
                "Constitutive Exon":19,    # FORMERLY 2
                "Exon Rank in Transcript":20,    # FORMERLY 3
                "cDNA coding start":21,    # FORMERLY 19
                "cDNA coding end":22,    # FORMERLY 20
                "Genomic coding start":23,    # FORMERLY 18
                "Genomic coding end":24,    # FORMERLY --
                "Ensembl Exon ID":25,    # FORMERLY 17
                "CDS Start":26,    # FORMERLY --
                "CDS End":27,    # FORMERLY --
                "Gene Biotype":28,    # FORMERLY --
                "Associated Gene DB":29}    # FORMERLY --

    genes = {}
    for line in f:
        if count == 0:    # headers
            headers = line.split("\t")
            print "headers = ", headers
        else:
            record = line.split("\t")
            record = [x.strip() for x in record]


            #===================================================================
            #
            # 0  "Exon Chr Start (bp)"          - by exon
            # 1  "Exon Chr End (bp)"            - by exon
            # 2  "Constitutive Exon"            - by exon
            # 3  "Exon Rank in Transcript"      - by exon
            # 4  "Ensembl Gene ID"          - by gene
            # 5  "Ensembl Transcript ID"      - by transcript
            # 6  "Ensembl Protein ID"         - by transcript
            # 7  "Chromosome Name"          - by gene
            # 8  "Gene Start (bp)"          - by gene
            # 9  "Gene End (bp)"            - by gene
            # 10 "Transcript Start (bp)"       - by transcript
            # 11 "Transcript End (bp)"         - by transcript
            # 12 "5' UTR End"                  - by transcript
            # 13 "3' UTR End"                  - by transcript
            # 14 "5' UTR Start"                - by transcript
            # 15 "3' UTR Start"                - by transcript
            # 16 "CDS Length"                  - by transcript
            # 17 "Ensembl Exon ID"               - by exon
            # 18 "Genomic coding start"        - by transcript
            # 19 "cDNA coding start"           - by transcript
            # 20 "cDNA coding end"             - by transcript
            #===================================================================

            # process record[4, 7, 8, 9]
            if record[fields["Ensembl Gene ID"]] not in genes:    # new record.
                g = {"gene":record[fields["Ensembl Gene ID"]],
                     "chr": record[fields["Chromosome Name"]],
                     "start":int(record[fields["Gene Start (bp)"]]),
                     "end":int(record[fields["Gene End (bp)"]]),
                     "strand":int(record[fields["Strand"]]),
                     "name":record[fields["Associated Gene Name"]],
                     "namelc":record[fields["Associated Gene Name"]].lower(),
                     "transcript_count":int(record[fields["Transcript count"]]),
                     "description":record[fields["Description"]]}
                if record[fields["Genomic coding start"]]:
                    g["genCodingstart"] = int(record[fields["Genomic coding start"]])
                if record[fields["Genomic coding end"]]:
                    g["genCodingend"] = int(record[fields["Genomic coding end"]])




                genes[record[fields["Ensembl Gene ID"]]] = g
            # process record[5,6,10,11,12,13,14,15,16,18,19,20]
            if "transcripts" not in genes[record[fields["Ensembl Gene ID"]]]:
                genes[record[fields["Ensembl Gene ID"]]]["transcripts"] = {}
            # print "transcripts = ", genes[record[fields["Ensembl Gene ID"]]]["transcripts"]
            if record[fields["Ensembl Transcript ID"]] not in genes[record[fields["Ensembl Gene ID"]]]["transcripts"]:
                t = {}
                if record[fields["Ensembl Protein ID"]]:
                    t["ens_pid"] = record[fields["Ensembl Protein ID"]]
                if record[fields["Transcript Start (bp)"]]:
                    t["start"] = int(record[fields["Transcript Start (bp)"]])
                if record[fields["Transcript End (bp)"]]:
                    t["end"] = int(record[fields["Transcript End (bp)"]])
                if record[fields["5' UTR End"]]:
                    t["5UTRend"] = int(record[fields["5' UTR End"]])
                if record[fields["3' UTR End"]]:
                    t["3UTRend"] = int(record[fields["3' UTR End"]])
                if record[fields["5' UTR Start"]]:
                    t["5UTRstart"] = int(record[fields["5' UTR Start"]])
                if record[fields["3' UTR End"]]:
                    t["3UTRstart"] = int(record[fields["3' UTR Start"]])
                if record[fields["CDS Length"]]:
                    t["CDSlen"] = int(record[fields["CDS Length"]])

                if record[fields["cDNA coding start"]]:
                    t["cDNAcodestart"] = int(record[fields["cDNA coding start"]])
                if record[fields["cDNA coding end"]]:
                    t["cDNAcodeend"] = int(record[fields["cDNA coding end"]])
                genes[record[fields["Ensembl Gene ID"]]]["transcripts"][record[fields["Ensembl Transcript ID"]]] = t
            # process record[0,1,2,3,17]
            if "exons" not in genes[record[fields["Ensembl Gene ID"]]]["transcripts"][record[fields["Ensembl Transcript ID"]]]:
                genes[record[fields["Ensembl Gene ID"]]]["transcripts"][record[fields["Ensembl Transcript ID"]]]["exons"] = {}
            if record[fields["Ensembl Exon ID"]] not in genes[record[fields["Ensembl Gene ID"]]]["transcripts"][record[fields["Ensembl Transcript ID"]]]["exons"]:
                e = {}
                if record[fields["Exon Chr Start (bp)"]]:
                    e["start"] = int(record[fields["Exon Chr Start (bp)"]])
                if record[fields["Exon Chr End (bp)"]]:
                    e["end"] = int(record[fields["Exon Chr End (bp)"]])
                if record[fields["Constitutive Exon"]]:
                    e["constitutive"] = int(record[fields["Constitutive Exon"]])
                if record[fields["Exon Rank in Transcript"]]:
                    e["number"] = int(record[fields["Exon Rank in Transcript"]])
                genes[record[fields["Ensembl Gene ID"]]]["transcripts"][record[fields["Ensembl Transcript ID"]]]["exons"][record[17]] = e
        count += 1

    # print genes.keys()
    # print genes['ENSG00000101574']['transcripts']
    print "genes parsed:", len(genes)
    print "size of genes:", sys.getsizeof(genes)
    print "attempting insert into database..."
    for gene in genes:
        a = mongo.insert("ensgenes", genes[gene])
    print "success! ", a
    print "creating indexes..."
    mongo.ensure_index("ensgenes", "gene")
    mongo.ensure_index("ensgenes", "name")
    mongo.ensure_index("ensgenes", [("chr", pymongo.ASCENDING), ("start", pymongo.ASCENDING), ("end", pymongo.ASCENDING)])
    print "success! "


    # rows = mongo.InsertBatchToDB("methylation", to_insert)
    # if rows == len(to_insert):
    #    print "final batch successfully inserted - %i rows processed" % count
    # else:
    #    print "final batch insert failed! - %i rows processed" % count


#     f.close()
#===============================================================================


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("tsvgenes", help = "The file name of the TSV beta file to import", type = str)
    parser.add_argument("-dbconfig", help = "An optional file to specify the database location - default is database.conf in MongoDB directory", type = str, default = None)
    parser.add_argument("-dbname", help = "name of the Database in the Mongo implementation to use - default is provided in the database.conf file specified", type = str, default = None)
    args = parser.parse_args()
    p = Parameters.parameter(args.dbconfig)
    if args.dbname:
        p.set("default_database", args.dbname)
    starttime = time.time()
    mongodb = Mongo_Connector.MongoConnector(p.get('server'), p.get('port'), p.get('default_database'))
    importObjectsSampleData(mongodb, args.tsvgenes)
    mongodb.close()
    print('Done in %s seconds') % int((time.time() - starttime))
