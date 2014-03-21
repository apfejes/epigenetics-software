'''
Created on 2013-05-23

@author: sperez, apfejes

'''
import os, sys
from numpy import log, mean, std
from math import sqrt
import math
import Svg_Builder
import time

_cur_dir = os.path.dirname(os.path.realpath(__file__))
_root_dir = os.path.dirname(_cur_dir)
_root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
from common_utilities import CreateListFromCursor
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import CommonUtils.Parameters as Parameters

sys.path.insert(0, _root_dir + os.sep + "Illustration")
# from .Annotations import showchipseq, showchipandmeth


from bson.objectid import ObjectId
# directory_for_svgs = "/home/sperez/Documents/svg_temp/"

class MongoEpigeneticsWrapper():
    '''A class to simplify plotting methylation and chipseq data from a mongo database'''

    def __init__(self, database, methylation, peaks):
        '''Performs the connection to the Mongo database.'''
        self.database = database
        self.p = Parameters.parameter()
        self.mongo = Mongo_Connector.MongoConnector(self.p.get('server'), self.p.get('port'), database)    # database changes based on interface value
        self.methylation = methylation
        self.peaks = peaks

        self.error_message = None
        self.svg_builder = None


    def query(self, parameters,
                sample_group = None,
                sample_label = None):
        '''Function performs the query on the database to retrieve information.'''
        # self.svg_builder.collection = collection

        start = parameters['start']
        end = parameters['end']
        if start == end or start > end or start < 0 or end < 0:
            self.error_message = 'Invalid start and end points.'
        else:
            self.error_message = ''    # contains error messages to pass to the server
        chromosome = parameters['chromosome']
        if isinstance(chromosome, int) or chromosome[0:3] != 'chr':
            parameters['chromosome'] = 'chr' + str(chromosome)

        # Make sure chr variable is in the right format

        self.svg_builder = Svg_Builder.Svg_Builder(self.methylation, self.peaks, start, end)

        if self.methylation:
            sample_ids = self.organize_samples_methylation(parameters['methylation_project'], sample_label, sample_group, parameters['groupby_selected'])
            cursor = self.finddocs_annotations(chromosome, start, end)    # get probe and annotation info for region queried
            docs = CreateListFromCursor(cursor)
            probes = self.getprobes(docs)    # get list of probe ids

            self.collectbetas(parameters['methylation_project'], sample_ids, probes)    # organize the beta values with sample info into a dictionary
            annotation_docs = docs

        if self.peaks:
            sample_ids = self.organize_samples_chipseq(parameters['chipseq_project'])
            cursor = self.finddocs_waves(sample_ids, chromosome, start, end, minh = parameters['minheight'], mins = parameters['minsigma'])    # get peak info for region queries
            docs = CreateListFromCursor(cursor)
            self.getwaves(docs, sample_ids, start, end)    # organize peak info into a dictionary
            if self.database == 'human_epigenetics':
                annotation_docs = self.finddocs_annotations(chromosome, start, end)    # get the gene annotations info
            else:
                annotation_docs = {}
        return annotation_docs

    def checkquery_tests(self, collection, project, chromosome):
        print "Checking validity of query inputs..."
        self.mongo.ensure_index(collection, 'chr')
        Chromosomes = self.mongo.distinct(collection, 'chr')
        if project != None:
            Projects = self.mongo.distinct(collection, "project")
        if chromosome not in Chromosomes:
            raise ValueError("Invalid chromosome name. Please choose from the following possible inputs:",
                             Chromosomes.encode("utf-8"))
        if project not in Projects:
            raise ValueError("Invalid project. Please choose from the following:", Projects)


    def checkquery(self, project, chromosome):
        '''Checks that query inputs are valid'''
        if self.methylation:
            self.checkquery_tests('methylation', project, chromosome)
        if self.peaks:
            self.checkquery_tests('waves', project, chromosome)
        return None


    def organize_samples_methylation(self, project, sample_label, sample_group, groupby_name):
        '''
        Finds the sample_ids of the project and sample group user is interested in
        saves a dictionary of the form {sample_id: (sample_label, sample_group)
        
        Sets the default group_by property of each dataset. 
        '''
        # print "project name = %s" % project
        project = [str(p) for p in project]
        if len(project) == 1:
            project = project[0]

        if groupby_name != 'project':    # if "All",then special case, don't use project in the query!
            samplesdocs = self.finddocs_samples_methylation(sample_group = groupby_name, project = project)
        # print "sampledocs %s" % (samplesdocs)
        else:
            samplesdocs = self.finddocs_samples_methylation(project = project,
                                sample_label = sample_label,
                                sample_group = groupby_name)

        if samplesdocs is None:
            self.error_message = 'No samples found'
            return {}

        sample_ids = {}
        if groupby_name in samplesdocs[0]:
            for doc in samplesdocs:
                sample_id = str(doc['sampleid'])
                if groupby_name in doc:
                    doc_sample_group = doc[groupby_name]
                    if doc_sample_group == sample_group or sample_group is None:
                        sample_ids[sample_id] = str(doc_sample_group)
        else:
            v = self.mongo.find_one("sample_groups", {"project":project}, {"_id":0, "compound":1})
            fields = v["compound"][groupby_name]
            for doc in samplesdocs:
                sample_id = str(doc['sampleid'])
                doc_sample_group = []
                for field in fields:
                    doc_sample_group.append(str(doc[field]))
                compoundkey = "-".join(doc_sample_group)
                sample_ids[sample_id] = compoundkey
        return sample_ids


    def organize_samples_chipseq(self, chip):
        '''
        Finds the sample_ids of the project and sample group user is interested in
        saves a dictionary of the form {sample_id: (sample_label, sample_group)
        
        Sets the default group_by property of each dataset. 
        '''

        samplesdocs = self.finddocs_samples_chipseq(chip)
        if samplesdocs is None:
            self.error_message = 'No samples found'
            return {}
        sample_ids = {}

        for doc in samplesdocs:
            sample_ids[str(doc['_id'])] = doc['sample_id'].encode('utf-8')
            # doc_chip = doc['sample_id'].encode('utf-8')    # using str() did not work.
        return sample_ids


    def finddocs_annotations (self, chromosome, start, end):

        '''Finds documents corresponding to collection and type of query'''

        if self.error_message != '' :    # If there are existing error messages, don't perform these operations.
            return {}
        collection = 'annotations'
        query_parameters = {}    # This dictionary will store all the query parameters
        query_parameters["chr"] = chromosome
        query_location = {}
        if end >= 0:
            query_location["$lte"] = end
        if start >= 0:
            query_location["$gte"] = start
        query_parameters["mapinfo"] = dict(query_location.items())
        # Decide which parameters to return
        return_chr = {'targetid': True, 'mapinfo':True, 'closest_tss':True, 'hil_cpg_island_name':True,
                      'closest_tss_1': True, 'ucsc_refgene_name':True, 'closest_tss_gene_name':True,
                      'regulatory_feature_group':True, 'regulatory_feature_name':True, 'n_snpcpg': True,
                      'n_snpprobe':True}
        # Decide how to sort the returned entries (make sure there is an index on the chosen sorting parameter)
        sortby, sortorder = 'mapinfo', 1

        return self.runquery(collection, query_parameters, return_chr, sortby, sortorder)


    def finddocs_waves(self, sample_ids, chromosome, start, end, minh = 0, mins = 0):

        '''Finds documents corresponding to collection and type of query
        
          sample_ids is a dictionary of sample _id's and unique names  (sample_id)
          It must be converted to an array for queries, unless the "All" parameter is used,
          in which case you don't need to use them for querying at all. 
        '''

        if self.error_message != '' :    # If there are existing error messages, don't perform these operations.
            return {}
        collection = 'waves'
        query_parameters = {}    # This dictionary will store all the query parameters

        samples = []
        for key in sample_ids:
            samples.append(ObjectId(key))

        query_parameters['chr'] = chromosome
        if (len(samples) > 1):
            query_parameters["sample_id"] = {"$in":samples}
        else:
            query_parameters["sample_id"] = samples[0]
        if start and end:
            extension = 500    # extend the region of query to catch peaks with tails in the region
            query_parameters["pos"] = {"$lte":end + extension, "$gte":start - extension}

        minh = float(minh)
        if (minh > 0):
            print "--->minh: ", minh
            query_parameters["height"] = {"$gte":minh}

        mins = float(mins)
        if (mins > 0):
            print "--->mins: ", mins
            query_parameters["stddev"] = {"$gte":mins}


        return_chr = {'_id': False, 'pos': True,
                      'height': True, 'stddev': True,
                      'sample_id': True}
        sortby, sortorder = 'height', (-1)
        # Will attempt to sort, will sort if not too large. This logic is in runquery
        return self.runquery(collection, query_parameters, return_chr, sortby, sortorder)

    def finddocs_samples_chipseq(self, sample_id, hide = True):

        '''Finds documents corresponding to collection and type of query
           chip should be either a single sample_id (sample name) or a list of sample_ids.
           
           All imported samples must have a "haswaves:true", must have a "use" 
           flag set to true, which can be overriden, and a sample_id, with a 
           unique identifier.
           '''

        if self.error_message != '' :    # If there are existing error messages, don't perform these operations.
            return {}
        collection = 'samples'
        return_chr = {'_id': True, 'sample_id':True}
        # query_parameters = {}    # This dictionary will store all the query parameters

        if sample_id == ["All"]:
            query_parameters = {"haswaves":True}
        elif isinstance(sample_id, list):
            query_parameters = {"haswaves":True, "sample_id":{"$in":sample_id}}

        else:
            query_parameters = {"haswaves":True, "sample_id":sample_id}
        # query_parameters = {"sample_id":{"$in":["02/08/2012_WT_IP_S9.6", "01/24/2012_WT_IP_S9.7", "04/12/2013_RNaseH_IP_S9.8", "04/12/2013_Sen1_IP_S9.9", "04/20/2013_RNaseH_IP_S9.10", "04/20/2013_Sen1_IP_S9.11"]}}
        if hide:
            query_parameters["hide"] = False    # show records with a {hide:false}
        else:
            return_chr['file_name'] = True
        print "---> finddocs_samples_chipseq, chip =  %s" % sample_id

        sortby, sortorder = 'sample_group', 1
        print "finding samples based on query :"
        print "---> Query Parameters: %s" % query_parameters
        print "---> return conditions: %s" % return_chr

        return self.runquery(collection, query_parameters, return_chr, sortby, sortorder)

    def finddocs_samples_methylation(self, project = None, sample_label = None,
                 sample_group = None):

        '''Finds documents corresponding to collection and type of query'''

        if self.error_message != '' :    # If there are existing error messages, don't perform these operations.
            return {}
        collection = 'samples'
        query_parameters = {}    # This dictionary will store all the query parameters
        # return_chr = {'_id': True, 'sampleid':True, 'project':True}
        # if sample_group != 'project':
        #    return_chr[sample_group] = True


        query_parameters['haswaves'] = {'$exists':False}
        if project != "All" and project != "Tissue":
            print "--->project = ", project
            if isinstance(project, list):
                query_parameters["project"] = {'$in':project}
            else :
                query_parameters["project"] = project

        if sample_label:
            query_parameters["sample_label"] = sample_label

        if sample_group == "tissuetype":
            query_parameters["tissuetype"] = {"$exists":True}


        sortby, sortorder = 'sample_group', 1
        print "finding samples based on query :"
        print "---> Query Parameters: %s" % query_parameters
        # print "---> return conditions: %s" % return_chr

        return self.runquery(collection, query_parameters, None, sortby, sortorder)


    def finddocs_methylation(self, project = None, sample_ids = None, probe_id = None, batch_size = None):

        '''Finds documents corresponding to collection and type of query'''

        if self.error_message != '' :    # If there are existing error messages, don't perform these operations.
            return {}
        collection = 'methylation3'
        query_parameters = {}    # This dictionary will store all the query parameters

        # Adding the different parameters of the query depending on the collection chosen
        if not project:
            return None
        else:
            query_parameters["project"] = project
        if sample_ids:
            query_parameters["sid"] = sample_ids
        if probe_id:
            query_parameters["pid"] = probe_id
        return_chr = {'pid':True, 'b':True, '_id':0}

        return self.runquery(collection, query_parameters, return_chr, batch_size = batch_size)

    def runquery(self, collection, query_parameters, return_chr, sortby = None, sortorder = None, batch_size = None):
        '''run a query to return records.'''
        print "\n Conducting query. "
        # print "   From the database %s and collection %s" % (self.database, collection)
        # print "   Find(%s)" % (query_parameters)    # Get documents corresponding to query and sort by sorting parameter
        if sortby:
            if self.mongo.find(collection, query_parameters, return_chr).count() < 100000:
                docs = self.mongo.find(collection, query_parameters, return_chr).sort(sortby, sortorder)
            else:
                docs = self.mongo.find(collection, query_parameters, return_chr)
        elif batch_size:
            docs = self.mongo.find(collection, query_parameters, return_chr)
        else:
            docs = self.mongo.find(collection, query_parameters, return_chr)

        if docs.count() == 0:
            warning = "    WARNING: The following query returned zero probes or documents!"
            warning += "\n    ---> Find in collection [%s] (%s)" % (collection, (str(query_parameters)))
            warning += "\n     use the checkquery() method to validate the inputs of your query."
            print warning

            # todo: warn if no data found
            return {}

        print "    --> Found %i documents." % docs.count()
        # return documents found
        return docs

    def getprobes(self, docs):
        '''Organises the probe locations/ids into a dictionary, saves prove info for svg_builder.'''
        probes = {}
        probes_inv = {}
        probe_details = {}
        if docs is None:
            self.svg_builder.error_message = 'No data here'
            return {}

        for doc in docs:
            if self.methylation:
                probes[str(doc['targetid'])] = doc['mapinfo']
                if doc['mapinfo'] not in probes_inv:
                    probes_inv[doc['mapinfo']] = str(doc['targetid'])
                det = {}
                det["n_snpcpg"] = doc["n_snpcpg"]
                det["n_snpprobe"] = doc["n_snpprobe"]
                probe_details[str(doc['targetid'])] = det

        self.svg_builder.probes_by_pos = probes_inv
        self.svg_builder.probe_details = probe_details
        return probes

    def collectbetas(self, projects, sample_ids, probes):
        '''Collects and bins methylation data, and pushes it into the svg_generating object.'''
        # Bin the beta values and collect their position
        pos_betas_dict = {}    # contains CpGs
        sample_peaks = {}    # contains average CpG value and std for samples from same Sample Group
        count = 0
        maxpos = 0

        if probes == {}:
            self.svg_builder.sample_peaks = {}
            self.svg_builder.pos_betas_dict = {}
            return

        probedata = self.finddocs_methylation(project = {"$in":projects}, probe_id = {'$in':probes.keys()}, batch_size = 20000)

        t0 = time.time()
        print "\n Start Timing Core Loop."
        for methyldata in probedata:
            count += 1
            pos = probes[methyldata['pid']]
            for sample, stype in sample_ids.iteritems():
                beta = methyldata['b'][sample]
                if math.isnan(beta):
                    continue
                if pos in pos_betas_dict:
                    pos_betas_dict[pos].append((beta, sample, stype))
                else:
                    pos_betas_dict[pos] = [(beta, sample, stype)]
                if pos in sample_peaks:
                    if stype in sample_peaks[pos]:
                        sample_peaks[pos][stype].append(beta)
                    else:
                        sample_peaks[pos][stype] = [beta]
                else:
                    sample_peaks[pos] = {stype:[beta]}
                if pos > maxpos:
                    maxpos = pos

        self.svg_builder.pos_betas_dict = pos_betas_dict

        tz = time.time() - t0
        if count > 0:
            print "    --> time taken - %f seconds" % (tz)
            print "    --> per record = %f ms" % ((tz / count) * 1000)
            print '\n    %s beta values were extracted.' % count
            print "    %i CpGs locations were found" % len(pos_betas_dict)

        for pos, type_dict in sample_peaks.iteritems():
            for stype, betas in type_dict.iteritems():
                m = mean(betas)
                s = std(betas)
                sample_peaks[pos].update({stype : (m, s)})
        self.svg_builder.sample_peaks = sample_peaks

        return


    def getwaves(self, docs, sample_ids, start, end):
        '''Collects and bins chipseq data, and pushes it into the svg_generating object.'''
        count = 0
        tail = 1
        maxpos = 0

        if docs == {}:
            self.svg_builder.waves = {}
            return None

        # This list will store the tuple (pos,height, std dev, sample id) as a value.
        waves = []
        # "tail" is min height of a tail to be included in the plot for a peak
        # which doesn't have its center in the region
        for doc in docs:
            pos, height, stddev, sample_id = doc['pos'], doc['height'], int(doc['stddev']), str(doc['sample_id'])
            # search for sample label name:
            doc_sample_group = sample_ids[sample_id]
            if start <= pos <= end:
                waves.append((pos, height, stddev, doc_sample_group))
                count += 1
            else:
                if not end:
                    dist_to_region = 0
                else:
                    dist_to_region = min(abs(pos - end), abs(start - pos))
                dist_from_peak_to_tail = sqrt((-2) * stddev * stddev * log(tail / height))
                if dist_from_peak_to_tail - dist_to_region >= 0:
                    waves.append((pos, height, stddev, doc_sample_group))
                    count += 1
            if pos > maxpos:
                maxpos = pos

        if count == 0:
            message = "    WARNING: None of peaks found in the query lie in the region!"
            print message
            # self.errorlog(error_message)
        else:
            print "   Only %i peaks were found to occur in region." % count
            self.svg_builder.waves = waves

        return None

    def getannotations(self, docs):
        '''Organizes the annotation information into a dictionary'''
        annotations = {}
        annotations['Islands'] = set([])
        annotations['feature'] = set([])

        for doc in docs:
            # Pull regulatory features' coordinate. Not plotting these yet.
            feature = str(doc['regulatory_feature_group'])
            feature_coord = str(doc['regulatory_feature_name'])
            if feature and feature_coord:
                feature_coord.split(':')[1].split('-')
            if doc['hil_cpg_island_name']:
                # cpg_class = doc['hil_cpg_class']
                # Parse CpG islands info of format (chr#_class:start-end)
                islands = doc['hil_cpg_island_name'].split(';')
                for island in islands:
                    if island != '.':
                        cpg_class, coord = island.split(':')
                        coord = coord.split('-')
                        coord = (int(coord[0]), int(coord[1]))
                        annotations['Islands'].add((coord, cpg_class))

            annotations['feature'].add((feature, feature_coord))

        print "\n    Annotations found:"
        for key, value in annotations.iteritems():
            print "        ", key, len(value), value

        self.svg_builder.annotations = annotations
        return None


    def find_genes(self, chromosome, start, end):
        '''given a region find all of the genes that overlap'''
        query = {"chr":chromosome, "end":{"$gt":start}, "start":{"$lt":end} }
        cursor = self.mongo.find("ensgenes", query)
        return CreateListFromCursor(cursor)

    def find_coords_by_gene (self, name):
        '''given the name of a gene, get the coordinates'''
        r = self.mongo.find_one("ensgenes", {"namelc":name.lower()}, {"chr":1, "start":1, "end":1, "_id":0})
        if r == None:
            return None
        else:
            return r

    def find_coords_by_probeid (self, name):
        '''given the name of a probe get the coordinates'''
        r = self.mongo.find_one("annotations", {"targetid":name.lower()}, {"chr":1, "mapinfo":1, "_id":0})
        if r == None:
            return None
        else:
            return r



