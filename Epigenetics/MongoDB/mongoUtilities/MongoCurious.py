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
        self.errorcount = 0

    def query(self,
                collection,
                chromosome,
                project = None,
                start = None,
                end = None,
                sample_type = None,
                sample_label = None,
                sample_id = None):
        '''Stores query inputs and parameters as an instance of MongoQuery'''

        self.collection = collection
        self.end = end
        self.start = start
            
        if isinstance(chromosome, int) or chromosome[0:3] != 'chr':
            chromosome = 'chr' + str(chromosome)
        self.chromosome = chromosome
        
        #First we collect the list of samples the user is interested in:
        self.sample_ids_list = self.organize_samples(project, sample_type, sample_label)
        
        #Conduct query and collect the data depending on which collection was chosen.
        if self.collection == 'methylation':
            cursor = self.finddocs(collection = 'annotations', project = project, sample_label = sample_label)
            docs = MongoCurious.parse_cursor(cursor)
            self.getprobes(docs)
            self.getannotations(docs)
            self.collectbetas()
        
        if self.collection == 'waves':
            docs = self.finddocs(collection = collection, project = project, sample_label = sample_label)
            MongoCurious.parse_cursor(docs)
            self.getwaves(docs)            
        
        return None
    
    @staticmethod
    def parse_cursor(cursor):
        docs =[]
        for doc in cursor:
            docs.append(doc)
        return docs

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


    def finddocs(self, collection, sample_ids_list = None, probe_id = None, project = None, sample_label = None, sample_type = None):
        '''Finds probes or documents corresponding to query'''
        #self.mongo.ensure_index(self.collection, 'start_position')    # for speed? to be tested...
        query_chr, query_location, query_samplabel, query_pos, query_sampgroup, query_project, query_probe, query_samplist = {}, {}, {}, {}, {}, {}, {}, {}

        # Preparing the different parameters of the query depending on the collection chosen
        if collection ==  "annotations":
            query_chr = {"chr":self.chromosome}
            #if project: query_project = {'project': project}
            if self.end and self.start: 
                query_location = {"mapinfo":{"$gte":self.start, "$lte":self.end }}
            #if sample_label: query_samplabel = {"sample_label":sample_label}
            #return_chr = {'_id': False, 'beta_value': True,
            #              'start_position': True, 'end_position': True,
            #              'sample_label': True}
            return_chr = {'targetid': True, 'mapinfo':True, 'closest_tss':True, 'hmm_island': True,
                          'closest_tss_1': True, 'ucsc_refgene_name':True, 'closest_tss_gene_name':True,
                          'regulatory_feature_group':True, 'regulatory_feature_name':True,'strand':True} 
            sortby, sortorder = 'mapinfo', 1
            
            
        elif collection == 'waves':
            query_chr = {'chr':self.chromosome}
            if project: query_project = {'project': project}
            if self.start and self.end:
                extension = 500    # extend the region of query to catch peaks with tails in the region
                query_pos = {"pos":{"$lte":self.end + extension, "$gte":self.start - extension}}
            if sample_label: query_samplabel = {"sample_label":sample_label}
            #if self.sample_group: query_sampgroup = {"Sample Group":self.sample_group}
            return_chr = {'_id': False, 'pos': True,
                          'height': True, 'stddev': True,
                          'sample_id': True}
            sortby, sortorder = 'height', (-1)

        elif collection =="samples":
            if project: query_project = {"project":project}
            if sample_label: query_samplabel = {"sample_label":sample_label}
            if sample_type: query_sampgroup = {"sample_group":sample_type}
            return_chr = {'_id': True, 'samplelabel': True, 
                          'project': True, 'sample_group': True}
            sortby, sortorder = 'sample_group', 1

        elif collection ==  "methylation":
            if sample_ids_list:
                query_samplist = {"sampleid":sample_ids_list}
            if probe_id: 
                query_probe = {"probeid":probe_id}
            return_chr = {'mval':True, 'sampleid': True, 'beta':True, 
                          'probeid':True}
            sortby, sortorder = 'sampleid', 1


        else: 
            print "Collection queried is either not supported or not in the database. Exiting..."
            sys.exit()
            
        query = dict(query_chr.items() + query_location.items() + query_probe.items()
                     + query_samplabel.items() + query_pos.items() + query_samplist.items()
                     + query_sampgroup.items() + query_project.items())
        print "\n Conducting query: "
        print "   From the database '{0}', and collection '{1}', ".format(self.database, collection)
        print "   Find(", query, ")"
        # Get probes corresponding to query and sort by starting positions for beta value binning
        docs = self.mongo.find(collection, query, return_chr).sort(sortby, sortorder)

        if docs.count() == 0:
            message  = "    WARNING: The following query return zero probes or documents!" 
            message  += "\n    ---> Find(" + str(query) + ")"
            message  += "\n     use the checkquery() method to validate the inputs of your query."
            self.errorlog(message)
            sys.exit()
            

        print "    --> Found %i documents." % docs.count()
        self.count = docs.count()
        self.docs = docs
        return docs

    def getannotations(self,docs):
        annotations = {}
        annotations['TSS'] = []
        annotations['Islands'] = []
        annotations['genes'] = []
        annotations['feature'] = []
        for doc in docs:
            tss1 = int(doc['closest_tss'])
            tss2 = int(doc['closest_tss_1'])
            gene = str(doc['ucsc_refgene_name'])
            if gene: gene = list(set(str(gene).split(';')))
            geneclosest = str(doc["closest_tss_gene_name"])
            if geneclosest : geneclosest = list(set(str(geneclosest).split(';')))
            feature = str(doc['regulatory_feature_group'])
            feature_coord = str(doc['regulatory_feature_name'])
            if feature_coord: feature_coord.split(':')[1].split('-')
            
            for genename in gene:
                if tss1 in range(self.start, self.end) and (genename,tss1) not in annotations['TSS']:
                    annotations['TSS'].append((genename,tss1))
                elif (genename,tss1) not in annotations['genes']:
                    annotations['genes'].append((genename, tss1))
            for genenameclosest in geneclosest:
                if (genenameclosest,tss2) not in annotations['genes']:
                    annotations['genes'].append((genenameclosest,tss2))
                    
            if doc['hmm_island']:
                coord = doc['hmm_island'].split(':')[1].split('-')
                island  = (int(coord[0]), int(coord[1]))
                if island not in annotations['Islands']: annotations['Islands'].append(island)
            
            if feature and (feature, feature_coord) not in annotations['feature']:
                annotations['feature'].append((feature, feature_coord))
                
        print "\n    Annotations found:"
        for key,value in annotations.iteritems():
            print "        ", key, len(value), value

        self.annotations = annotations
        return None
    
    def organize_samples(self, project, queried_sample_type, queried_sample_label):
        #Finds the sample_ids of the project and sample group user is interested in
        #saves a dictionary of the form {sample_id: (sample_label, sample_type)
        
        samplesdocs = self.finddocs(collection = 'samples', project = project, sample_label = queried_sample_label, sample_type = queried_sample_type)
        
        sample_ids = {}
        for doc in samplesdocs:
            sample_id = str(doc['_id'])
            sample_type = doc['sample_group']
            sample_label = doc['samplelabel']
            if sample_type == queried_sample_type or queried_sample_type == None: 
                if queried_sample_label == sample_label or queried_sample_label == None:
                    sample_ids[sample_id] = (sample_label, sample_type)
            
        return sample_ids
        
    def getprobes(self,docs):
        probes = {}
        for doc in docs:
            if self.collection == 'methylation':
                probes[str(doc['targetid'])] = doc['mapinfo']
        self.probes = probes
        return None
        
    def collectbetas(self):
        '''Collects and bins methylation data'''

        # Bin the beta values and collect their position
        pos_betas_dict = {} #contains CpGs
        sample_peaks = {}   #contains average CpG value and std for samples from same Sample Group
        count = 0
        sample_ids = self.sample_ids_list
        probes = self.probes
        
        probedata = self.finddocs(sample_ids_list = {"$in":sample_ids.keys()}, probe_id = {'$in':probes.keys()}, collection = self.collection)
        for methyldata in probedata:
            sample_id = str(methyldata['sampleid'])
            sample = sample_ids[sample_id][0]
            stype = sample_ids[sample_id][1]
            beta = methyldata['beta']
            #mval = methyldata['mval'] #unused currently
            pos = probes[methyldata['probeid']]
            #print pos, sample, stype, beta
            if pos in pos_betas_dict:
                pos_betas_dict[pos].append((beta, sample, stype))
            else:
                pos_betas_dict[pos] =[(beta, sample, stype)]
            count += 1
            if pos in sample_peaks:
                if stype in sample_peaks[pos]:
                    sample_peaks[pos][stype].append(beta)
                else:
                    sample_peaks[pos][stype] = [beta]
            else:
                sample_peaks[pos]={stype:[beta]}
                
                
        print '\n    %s probes\' beta values were extracted.' % count
        print "    %i CpGs locations were found" % len(pos_betas_dict)
        
        #print pos_betas_dict
        self.pos_betas_dict = pos_betas_dict

        for pos, type_dict in sample_peaks.iteritems():
            for stype, betas in type_dict.iteritems():
                m = mean(betas)
                s = std(betas)
                sample_peaks[pos].update({stype : (m,s)})
                        
        #print sample_peaks
        self.sample_peaks = sample_peaks

        if self.start == None:
            self.start = min(pos_betas_dict.keys()) #slow and could be improve
            #This might work instead: self.start = pos_betas_dict.keys()[0]
            
            print "    New start position:", self.start
        if self.end == None:
            self.end = max(pos_betas_dict.keys()) #slow and could be improved
            print "    New end position:", self.end
         
        
        return None


    def getwaves(self):
        count = 0
        tail = 1
        # This list will store the tuple (pos,height, std dev, sample id) as a value.
        waves = []
        # "tail" is min height of a tail to be included in the plot for a peak
        # which doesn't have its center in the region
        for doc in self.docs:
#            if isinstance(doc['stddev'], basestring): int()
            pos, height, stddev, sample_id = doc['pos'], doc['height'], int(doc['stddev']), doc['sample_id']
            #search for sample label name:
            sample_id = ObjectId(sample_id)
            sample_label = self.mongo.find('samples', {'_id':sample_id},{'chip':True})[0]['chip']
            #print sample_label
            # append all peaks with a center in the region
            if self.start <= pos <= self.end:
                waves.append((pos, height, stddev, sample_label))
                count += 1
            else:
                dist_to_region = min(abs(pos - self.end), abs(self.start - pos))
                dist_from_peak_to_tail = sqrt((-2) * stddev * stddev * log(tail / height))
                if dist_from_peak_to_tail - dist_to_region >= 0:
                    waves.append((pos, height, stddev, sample_label))
                    count += 1
                # else: print "         Not included:    ", pos, height, stddev,
        if count == 0:
            message = "    WARNING: None of peaks found in the query lie in the region!"
            self.errorlog(message)
        else:
            print "   Only %i peaks were found to occur in region." % count
            self.waves = waves
            self.Query['waves'] = waves
        
        #self.annotations = self.getannotations() 
        
        return None


    def svg(self, filename = None, title = None,
            color = None, to_string = False,
            get_elements = False, length = 200.0,
            margin = 20.0, width = 60.0):
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
                                                      length, margin, width)
            drawing.build()
        if self.collection == "waves":
            drawing = chipseqplot.ChipseqPlot(filename, title, self.waves,
                                              self.start, self.end, self.annotations,
                                              length, margin, width)
            drawing.build()

        if to_string:
            print " Returning svg as a unicode string"
            drawing.add_legends()
            z = drawing.to_string()
            drawing= None
        elif get_elements:
            z = drawing.get_elements()
            print " Returning %i svg elements" % len(z)
            drawing= None
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
    
    def errorlog(self, errormessage): 
        #returns error message to server
        self.errorcount +=1
        print errormessage
        return errormessage
        