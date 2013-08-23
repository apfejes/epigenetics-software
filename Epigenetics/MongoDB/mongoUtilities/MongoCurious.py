'''
Created on 2013-05-23

@author: sperez

'''
from time import time
import os, sys
from numpy import log, mean, std
from math import sqrt

_cur_dir = os.path.dirname(os.path.realpath(__file__))
_root_dir = os.path.dirname(_cur_dir)
_root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
from common_utilities import CreateListFromCursor

sys.path.insert(0, _root_dir + os.sep + "Illustration")
import ChipseqPlot as chipseqplot
import MethylationPlot as methylationplot

from bson.objectid import ObjectId

directory_for_svgs = "/home/sperez/Documents/svg_temp/"



class MongoCurious():
    '''A class to simplify plotting methylation and chipseq data from a mongo database'''
    def __init__(self,
                database):
        '''Connects to database'''
        self.database = database
        self.mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, database)
        # self.errorcount = 0

        self.pos_betas_dict = None
        self.collection = None
        self.chromosome = None
        self.sample_peaks = None
        self.end = None
        self.start = None
        self.waves = None
        self.annotations = None

    def query(self,
                collection,
                chromosome,
                start,
                end,
                chip = None,
                project = None,
                sample_group = None,
                sample_label = None,
                sample_id = None):
        '''remove sample_id, if not used'''
        self.collection = collection
        if end: end = int(end)
        else: end = None
        self.end = end
        if start: start = int(start)
        else: start = 0
        self.start = start

        # Make sure chr variable is in the right format
        if isinstance(chromosome, int) or chromosome[0:3] != 'chr':
            chromosome = 'chr' + str(chromosome)
        self.chromosome = chromosome

        # First we collect the list of samples the user is interested in:
        sample_ids = self.organize_samples(project, sample_label, sample_group, chip)
        # print '\n    Sample_ids list:', sample_ids

        # Conduct query and collect the data depending on which collection was chosen.
        if self.collection == 'methylation':
            cursor = self.finddocs('annotations')    # get probe and annotation info for region queried
            docs = CreateListFromCursor(cursor)
            probes = self.getprobes(docs)    # get list of probe ids
            self.collectbetas(sample_ids, probes)    # organize the beta values with sample info into a dictionary
            t0 = time()
            self.getannotations(docs)    # organize the gene annotations in a dictionary
            print 'Annotation time:', time() - t0

        if self.collection == 'waves':
            docs = self.finddocs(collection = collection, chip = chip, sample_ids = sample_ids)    # get peak info for region queried
            self.getwaves(docs, sample_ids)    # organize peak info into a dictionary
            if self.database == 'human_epigenetics':
                annotations_docs = self.finddocs(collection = 'annotations')    # get the gene annotations info
                self.getannotations(annotations_docs)    # organize the gene annotations in a dictionary

        return None

    def checkquery(self, project, chromosome):
        '''Checks that query inputs are valid'''
        t0 = time()
        self.mongo.ensure_index(self.collection, 'chr')
        print "Checking validity of query inputs..."

        Chromosomes = self.mongo.distinct(self.collection, 'chr')
        if chromosome not in Chromosomes:
            raise ValueError("Invalid chromosome name. Please choose from the following possible inputs:",
                             Chromosomes.encode("utf-8"))

        if project != None:
            Projects = self.mongo.distinct(self.collection, "project")
            if project not in Projects:
                raise ValueError("Invalid project. Please choose from the following:", Projects)
        print "Input check done in %i seconds." % round(time() - t0, 1)
        return None


    def organize_samples(self, project, sample_label, sample_group, chip):
        # Finds the sample_ids of the project and sample group user is interested in
        # saves a dictionary of the form {sample_id: (sample_label, sample_group)

        samplesdocs = self.finddocs(collection = 'samples', project = project,
                                    sample_label = sample_label,
                                    sample_group = sample_group,
                                    chip = chip)

        sample_ids = {}
        for doc in samplesdocs:
            sample_id = str(doc['_id'])

            if self.collection == 'waves':
                if self.database == 'yeast_epigenetics':
                    doc_chip = str(doc['type (ip, mock, input)'])
                else:
                    doc_chip = str(doc['chip'])
                if doc_chip == chip or chip is None:
                    sample_ids[sample_id] = doc_chip

            if self.collection == 'methylation':
                doc_sample_group = doc['sample_group']
                doc_sample_label = doc['samplelabel']
                if doc_sample_group == sample_group or sample_group is None:
                    if doc_sample_label == sample_label or sample_label is None:
                        sample_ids[sample_id] = (doc_sample_label, doc_sample_group)

        return sample_ids


    def finddocs(self, collection, sample_ids = None,
                 probe_id = None, project = None, sample_label = None,
                 sample_group = None, chip = None):

        '''Finds documents corresponding to collection and type of query'''

        # This dictionary will store all the query parameters
        query_parameters = {}

        # Adding the different parameters of the query depending on the collection chosen
        if collection == "annotations":
            query_parameters["chr"] = self.chromosome
            if self.end and self.start:
                query_parameters["mapinfo"] = {"$gte":self.start, "$lte":self.end }
            # Decide which parameters to return
            return_chr = {'targetid': True, 'mapinfo':True, 'closest_tss':True, 'hil_cpg_island_name':True,
                          'closest_tss_1': True, 'ucsc_refgene_name':True, 'closest_tss_gene_name':True,
                          'regulatory_feature_group':True, 'regulatory_feature_name':True}
            # Decide how to sort the returned entries (make sure there is an index on the chosen sorting parameter)
            sortby, sortorder = 'mapinfo', 1

        elif collection == 'waves':
            query_parameters['chr'] = self.chromosome
            if sample_ids:
                ids = []
                for item in sample_ids.keys():
                    ids.append(ObjectId(item))
                query_parameters["sample_id"] = {"$in":ids}
            if project: query_parameters['project'] = project
            if self.start and self.end:
                extension = 500    # extend the region of query to catch peaks with tails in the region
                query_parameters["pos"] = {"$lte":self.end + extension, "$gte":self.start - extension}
            return_chr = {'_id': False, 'pos': True,
                          'height': True, 'stddev': True,
                          'sample_id': True}
            sortby, sortorder = 'height', (-1)

        elif collection == "samples":
            if self.collection == 'waves':
                if chip: 
                    if self.database == 'yeast_epigenetics':
                        query_parameters["type  (ip, mock, input)"] = chip
                    else: 
                        query_parameters["chip"] = chip
                else: query_parameters['haswaves'] = True
            elif self.collection == 'methylation':
                query_parameters['haswaves'] = {'$exists':False}
                if project: query_parameters["project"] = project
                if sample_label: query_parameters["sample_label"] = sample_label
                if sample_group: query_parameters["sample_group"] = sample_group
            return_chr = {'_id': True, 'samplelabel': True, 'type (ip, mock, input)':True,
                              'project': True, 'sample_group': True, 'chip':True}
            sortby, sortorder = 'sample_group', 1

        elif collection == "methylation":
            if sample_ids:
                query_parameters["sampleid"] = sample_ids
            if probe_id:
                query_parameters["probeid"] = probe_id
            return_chr = {'mval':True, 'sampleid': True, 'beta':True,
                          'probeid':True}
            sortby, sortorder = None, None

        else:
            print "Collection queried is either not supported or not in the database. Exiting..."
            sys.exit()

        print "\n Conducting query: "
        print "   From the database '{0}', and collection '{1}', ".format(self.database, collection)
        print "   Find(", query_parameters, ")"
        # Get documents corresponding to query and sort by sorting parameter
        if sortby:
            docs = self.mongo.find(collection, query_parameters, return_chr).sort(sortby, sortorder)
        else:
            docs = self.mongo.find(collection, query_parameters, return_chr)

        if docs.count() == 0:
            message = "    WARNING: The following query return zero probes or documents!"
            message += "\n    ---> Find(" + str(query_parameters) + ")"
            message += "\n     use the checkquery() method to validate the inputs of your query."
            # self.errorlog(message)
            print message
            sys.exit()

        print "    --> Found %i documents." % docs.count()
        # return documents found
        return docs

    def getprobes(self, docs):
        '''Organises the probe locations/ids into a dictionary'''
        probes = {}
        for doc in docs:
            if self.collection == 'methylation':
                probes[str(doc['targetid'])] = doc['mapinfo']
        return probes

    def collectbetas(self, sample_ids, probes):
        '''Collects and bins methylation data'''

        # Bin the beta values and collect their position
        pos_betas_dict = {}    # contains CpGs
        sample_peaks = {}    # contains average CpG value and std for samples from same Sample Group
        count = 0
        maxpos = 0

        probedata = self.finddocs(sample_ids = {"$in":sample_ids.keys()}, probe_id = {'$in':probes.keys()}, collection = self.collection)

        for methyldata in probedata:
            sample_id = str(methyldata['sampleid'])
            sample = sample_ids[sample_id][0]
            stype = sample_ids[sample_id][1]
            beta = methyldata['beta']
            # mval = methyldata['mval'] #unused currently
            pos = probes[methyldata['probeid']]
            if pos in pos_betas_dict:
                pos_betas_dict[pos].append((beta, sample, stype))
            else:
                pos_betas_dict[pos] = [(beta, sample, stype)]
            count += 1
            if pos in sample_peaks:
                if stype in sample_peaks[pos]:
                    sample_peaks[pos][stype].append(beta)
                else:
                    sample_peaks[pos][stype] = [beta]
            else:
                sample_peaks[pos] = {stype:[beta]}
            if pos > maxpos:
                maxpos = pos

        print '\n    %s probes\' beta values were extracted.' % count
        print "    %i CpGs locations were found" % len(pos_betas_dict)

        self.pos_betas_dict = pos_betas_dict

        for pos, type_dict in sample_peaks.iteritems():
            for stype, betas in type_dict.iteritems():
                m = mean(betas)
                s = std(betas)
                sample_peaks[pos].update({stype : (m, s)})

        self.sample_peaks = sample_peaks

        if self.end is None:
            self.end = maxpos
            print "    New end position:", self.end


        return None


    def getwaves(self, docs, sample_ids):
        count = 0
        tail = 1
        maxpos = 0

        # This list will store the tuple (pos,height, std dev, sample id) as a value.
        waves = []
        # "tail" is min height of a tail to be included in the plot for a peak
        # which doesn't have its center in the region
        for doc in docs:
            pos, height, stddev, sample_id = doc['pos'], doc['height'], int(doc['stddev']), str(doc['sample_id'])
            # search for sample label name:
            doc_sample_group = sample_ids[sample_id]
            if self.start <= pos <= self.end:
                waves.append((pos, height, stddev, doc_sample_group))
                count += 1
            else:
                if not self.end: dist_to_region = 0
                else: dist_to_region = min(abs(pos - self.end), abs(self.start - pos))
                dist_from_peak_to_tail = sqrt((-2) * stddev * stddev * log(tail / height))
                if dist_from_peak_to_tail - dist_to_region >= 0:
                    waves.append((pos, height, stddev, doc_sample_group))
                    count += 1
            if pos > maxpos:
                maxpos = pos

        if self.end is None:
            self.end = maxpos
            print "    New end position:", self.end

        if count == 0:
            message = "    WARNING: None of peaks found in the query lie in the region!"
            print message
            # self.errorlog(message)
        else:
            print "   Only %i peaks were found to occur in region." % count
            self.waves = waves

        return None

    def getannotations(self, docs):
        '''Organizes the annotation information into a dictionary'''
        annotations = {}
        annotations['TSS'] = {}
        annotations['Islands'] = set([])
        annotations['genes'] = set([])
        annotations['feature'] = set([])

        for doc in docs:
            tss1 = int(doc['closest_tss'])
            tss2 = int(doc['closest_tss_1'])
            gene = str(doc['ucsc_refgene_name'])
            if gene: gene = list(set(str(gene).split(';')))
            geneclosest = str(doc["closest_tss_gene_name"])
            if geneclosest : geneclosest = list(set(str(geneclosest).split(';')))
            feature = str(doc['regulatory_feature_group'])
            feature_coord = str(doc['regulatory_feature_name'])
            if feature and feature_coord: feature_coord.split(':')[1].split('-')

            for genename in gene:
                if tss1 in range(self.start, self.end):
                    annotations['TSS'][tss1] = genename
                else: annotations['genes'].add((genename, tss1))
            for genenameclosest in geneclosest:
                annotations['genes'].add((genenameclosest, tss2))

            # if doc['hmm_island']:
            #    coord = doc['hmm_island'].split(':')[1].split('-')
            #    island = (int(coord[0]), int(coord[1]))
            #    annotations['Islands'].add(island)

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

        self.annotations = annotations
        return None



    def svg(self, filename = None, title = None,
            color = None, to_string = False,
            get_elements = False, LENGTH = 200.0,
            MARGIN = 20.0, WIDTH = 60.0):
        ''' Plots the data using different SVG modules in Epigenetics/Illustrations
            Saves the plot as an .svg file or a svg string for webserver rendering
        '''
        if filename:
            if filename[-4:len(filename)] != '.svg':
                filename += '.svg'
            filename = directory_for_svgs + filename
        elif not get_elements: filename = "test.svg"

        if self.collection == "methylation":
            drawing = methylationplot.MethylationPlot(filename, title, self.sample_peaks,
                                                      self.pos_betas_dict, self.annotations,
                                                      color, self.start, self.end,
                                                      LENGTH, MARGIN, WIDTH)
            drawing.build()
        if self.collection == "waves":
            drawing = chipseqplot.ChipseqPlot(filename, title, self.waves,
                                              self.start, self.end, self.annotations,
                                              LENGTH, MARGIN, WIDTH)
            drawing.build()

        if to_string:
            print " Returning svg as a unicode string"
            drawing.add_legends()
            z = drawing.to_string()
            drawing = None
        elif get_elements:
            z = drawing.get_elements()
            print " Returning %i svg elements" % len(z)
            drawing = None
        elif filename and not to_string and not get_elements:
            print " Making svg file \"%s\"\n" % filename
            drawing.add_legends()
            z = drawing
            z.save()
            drawing = None
        else:
            print "No filename specified. Returning the SVG object with legends"
            drawing.add_legends()
            z = drawing
            drawing = None
        return z

# Error function below needs testing




    def errorlog(self, errormessage):
        # returns error message to server
        # self.errorcount += 1
        print errormessage
        return errormessage
