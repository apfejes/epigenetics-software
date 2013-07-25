'''
Created on 2013-05-23

@author: sperez

'''
from time import time
import os, sys
from numpy import log, mean, std
from math import sqrt

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
_root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
import MongoQuery
sys.path.insert(0, _root_dir + os.sep + "Illustration")
import ChipseqPlot as chipseqplot
import MethylationPlot as methylationplot

from bson.objectid import ObjectId

class MongoCurious():
    '''A class to simplify plotting methylation and chipseq data from a mongo database'''
    def __init__(self,
                database = None):
        '''Connects to database'''
        if database == None:
            raise ValueError("Please specify a database.")
        else: self.database = database
        self.mongo = Mongo_Connector.MongoConnector('kruncher.cmmt.ubc.ca', 27017, self.database)

    def query(self,
                collection = None,
                chromosome = None,
                start = None,
                end = None,
                sample_type = None,
                sample_label = None,
                sample_id = None,
                project = None):
        '''Stores query inputs and parameters as an instance of MongoQuery'''
        Query = MongoQuery.MongoQuery()
        if collection == None:
            raise ValueError("Please specify a collection.")
        self.collection = collection
        Query['database'] = self.database
        Query['collection'] = self.collection
        Query['project'] = project
        self.project = project
        Query['sample label'] = sample_label
        self.sample_label = sample_label
        Query['sample type'] = sample_type
        self.sample_type = sample_type
        Query['sample id'] = sample_id
        self.sample_id = sample_id
        self.sample_dictionary = None
        if collection != 'samples':
            if start:
                Query['start'] = int(start)
                self.start = int(start)
            else: self.start =None
            if end:
                Query['end'] = int(end)
                self.end = int(end)
            else:
                self.end = None
            if chromosome == None:
                raise ValueError("Please specificy a chromosome.")
            if isinstance(chromosome, basestring):
                Query['chromosome'] = chromosome
                self.chromosome = chromosome
            elif isinstance(chromosome, int):
                    Query['chromosome'] = 'chr' + str(chromosome)
                    self.chromosome = chromosome
            self.sample_label_list = self.creategroups()
            Query['sample label list'] = self.sample_label_list
            Query['sample_dictionary'] = self.sample_dictionary
        self.Query = Query
        if self.collection == 'methylation':
            collection = 'annotations'
        else: collection = self.collection
        self.docs = self.finddocs(collection = collection)
        return self.Query

    def checkquery(self):
        '''Checks that query inputs are valid'''
        t0 = time()
        self.mongo.ensure_index(self.collection, 'chr')
        print "Checking validity of query inputs..."

        Chromosomes = self.mongo.distinct(self.collection, 'chr')
        if self.chromosome not in Chromosomes:
            raise ValueError("Invalid chromosome name. Please choose from the following possible inputs:",
                             Chromosomes.encode("utf-8"))

        if self.project != None:
            Projects = self.mongo.distinct(self.collection, "project")
            if self.project not in Projects:
                raise ValueError("Invalid project. Please choose from the following:", Projects)
        print "Input check done in %i seconds." % round(time() - t0, 1)
        return None


    def finddocs(self, probe_id = None, collection = None):
        '''Finds probes or documents corresponding to query'''
        #self.mongo.ensure_index(self.collection, 'start_position')    # for speed? to be tested...
        query_chr, query_location, query_samplabel, query_pos, query_sampgroup, query_project, query_probe = {}, {}, {}, {}, {}, {}, {}

        # Preparing the different parameters of the query depending on the collection chosen
        if collection ==  "annotations":
            query_chr = {"chr":self.chromosome}
            #if self.project: query_project = {'project': self.project}
            if self.end and self.start: 
                query_location = {"mapinfo":{"$gte":self.start, "$lte":self.end }}
            #if self.sample_label: query_samplabel = {"sample_label":self.sample_label}
            #return_chr = {'_id': False, 'beta_value': True,
            #              'start_position': True, 'end_position': True,
            #              'sample_label': True}
            return_chr = {'targetid': True, 'mapinfo':True}
            sortby, sortorder = 'mapinfo', 1

        elif collection == "waves":
            collection = 'waves'
            query_chr = {'chr':self.chromosome}
            if self.project: query_project = {'project': self.project}
            if self.start and self.end:
                extension = 500    # extend the region of query to catch peaks with tails in the region
                query_pos = {"pos":{"$lte":self.end + extension, "$gte":self.start - extension}}
            if self.sample_label: query_samplabel = {"sample_label":self.sample_label}
            #if self.sample_group: query_sampgroup = {"Sample Group":self.sample_group}
            return_chr = {'_id': False, 'pos': True,
                          'height': True, 'stddev': True,
                          'sample_id': True}
            sortby, sortorder = 'height', (-1)

        elif collection =="samples":
            if self.project: query_project = {"project":self.project}
            if self.sample_label: query_samplabel = {"sample_label":self.sample_label}
            return_chr = {'_id': False, 'sample_label': True,
                          'project': True, 'Sample Group': True}
            sortby, sortorder = 'sample_label', 1

        elif collection ==  "methylation":
            if self.project: query_project = {'project': self.project}
            if probe_id: 
                query_probe = {"probe_id":probe_id}
            if self.sample_label: query_samplabel = {"sample_label":self.sample_label}
            return_chr = {'beta_value':True, 'sample_label': True, 'project':True, 
                          'probe_id':True}
            sortby, sortorder = 'sample_label', 1


        else: 
            print "Collection queried is either not supported or not in the database. Exiting..."
            sys.exit()
            
        query = dict(query_chr.items() + query_location.items() + query_probe.items()
                     + query_samplabel.items() + query_pos.items()
                     + query_sampgroup.items() + query_project.items())
        print "\n Conducting query: "
        print "   From the database '{0}', and collection '{1}', ".format(self.database, collection)
        print "   Find(", query, ")"
        # Get probes corresponding to query and sort by starting positions for beta value binning
        docs = self.mongo.find(collection, query, return_chr).sort(sortby, sortorder)

        if docs.count() == 0:
            print("    WARNING: The following query return zero probes or documents!")
            print "    ---> Find(", query, ")"
            print "     use the checkquery() method to validate the inputs of your query."
            sys.exit()

        print " Found %i documents." % docs.count()
        self.count = docs.count()
        self.Query['cursor'] = docs
        return docs


    def creategroups(self):
        '''
        Separate samples into 'groups' according to a particular feature and sample_type like disease
        or control.
        sample_label_list is a list of sample labels with the desired sample_type of that feature.
        '''
        print "    Creating sample groups..."
        if self.project == "down":
            if self.sample_type not in ["Control", "DS",None]: self.sample_type = str(raw_input(
                            "Please specify a sample type: \"Control\" or \"DS\"?"))
            if self.sample_type in ["Control", "DS"]:
                feature = 'Sample Group'
                sample_label_list = self.sample_dict(project = self.project, feature = feature)[self.sample_type]

        if self.project == "kollman":
            if self.sample_type not in ["unstimulated", "listeria", None]: self.sample_type = str(raw_input(
                            "Please specify a sample type: \"unstimulated\" or \"listeria\"?"))
            if self.sample_type in ["unstimulated", "listeria"]:
                feature = 'stimulation'
                sample_label_list = self.sample_dict(project = self.project, feature = feature)[self.sample_type]
        
        if self.project == "gecko":
            if self.sample_type not in ['BUCCAL','BLOOD SPOT', 'PBMC', None]: self.sample_type = str(raw_input(
                            "Please specify a sample type: \"BLOOD SPOT\" or \"BUCCAL\" or \"PBMC\"?"))
            if self.sample_type in ['BUCCAL','BLOOD SPOT', 'PBMC']:
                feature = 'Sample Group'
                sample_label_list = self.sample_dict(project = self.project, feature = feature)[self.sample_type]

        else:
            sample_dictionary = dict(self.sample_dict(project = 'gecko', feature = 'Sample Group').items() +
                                 self.sample_dict(project = 'down', feature = 'Sample Group').items() +
                                 self.sample_dict(project = 'kollman', feature = 'stimulation').items())
            self.sample_dictionary = sample_dictionary
            sample_label_list = []
            for type in sample_dictionary.keys():
                sample_label_list.extend(sample_dictionary[type])
            print sample_dictionary
            
#         if self.project == "All":
#             if self.sample_type != "control" or self.sample_type != None:
#                 print "The sample type \"", self.sample_type, "\" is invalid."
#                 self.sample_type = str(raw_input("Please specify a sample type: \"control\" or \"disease\"?"))
#             if self.sample_type == "control" or self.sample_type == None:
#                 sample_label_list = self.sample_dict(project = "kollman", feature = "stimulation")["unstimulated"]
#                 sample_label_list.append(self.sample_dict(project = "down", feature = "Sample Group")["Control"])
#                 sample_label_list.append(self.sample_dict(project = "kollman", feature = "stimulation",
#                                     nottype = ["unstimulated", "listeria"]))
#                 sample_label_list.append(self.sample_dict(project = "down", feature = "Sample Group",
#                                     nottype = ["Control", "DS"]))
#             if self.sample_type == "disease":
#                 sample_label_list = self.sample_dict(project = "kollman", feature = "stimulation")["listeria"]
#                 sample_label_list.append(self.sample_dict(project = "down", feature = "Sample Group")["DS"])

        if self.sample_type:
            print "    The sample labels with sample type", self.sample_type, " are:", sample_label_list
        return sample_label_list

    def sample_dict(self, project, feature, nottype = None):
        '''
        For a particular feature (for example, disease in Down Syndrome experiments) return a dictionary
        structured as {sample_type: sample_label} where sample_type is "control" or "diseased
        '''

        print "    Appending labels for project", project, "and", feature
        #self.mongo.ensure_index("samples", project)    # For speed
        #self.mongo.ensure_index("samples", feature)

        if nottype != None:
            add_query = {feature:{"$ne":nottype[0], "$ne":nottype[1]}}
            findQuery = dict({'project': project}.items() + add_query.items())
        else: findQuery = {'project': project}
        returnQuery = {feature: True, '_id': False, 'sample_label': True}

        samples = self.mongo.find("samples",
                             findQuery, returnQuery).sort(feature, 1)
                             
        sample_dictionary = {}
        for doc in samples:
            type = str(doc[feature])
            sample = str(doc['sample_label'])
            if type in sample_dictionary:
                sample_dictionary[type].append(sample)
            else:
                sample_dictionary[type] = [sample]
        self.sample_dictionary = sample_dictionary
        print sample_dictionary
        return sample_dictionary

    def type(self,sample):
        #inneficient way to look up the sample type of a sample.
        if self.sample_dictionary:
            for type, sample_list in self.sample_dictionary.iteritems():
                if sample in sample_list:
                    return type
        else: return None
        
    def collectbetas(self, group_samples = True):
        '''Collects and bins methylation data'''

        # Bin the beta values and collect their position
        pos_betas_dict = {} #contains CpGs
        sample_peaks = {}   #contains average CpG value and std for samples from same Sample Group
        count = 0
        probes = {}
        for doc in self.docs:
            probes[str(doc['targetid'])] = doc['mapinfo']
            
        probedata = self.finddocs(probe_id = {'$in':probes.keys()}, collection = self.collection)
        for methyldata in probedata:
            sample = str(methyldata['sample_label'])
            beta = methyldata['beta_value']
            pos = probes[methyldata['probe_id']]
            print pos, sample, beta
            type = self.type(sample) #not very efficient since iterating through the dictionary to get key from value.
            if pos in pos_betas_dict:
                pos_betas_dict[pos].append((beta, sample, type))
            else:
                pos_betas_dict[pos] =[(beta, sample, type)]
            count += 1
            if pos in sample_peaks:
                if type in sample_peaks[pos]:
                    sample_peaks[pos][type].append(beta)
                else:
                    sample_peaks[pos][type] = [beta]
            else:
                sample_peaks[pos]={type:[beta]}
                
                
        print '\n    %s probes\' beta values were extracted.' % count
        print "    %i CpGs locations were found" % len(pos_betas_dict)
        
        #print pos_betas_dict
        self.pos_betas_dict = pos_betas_dict

        for pos, type_dict in sample_peaks.iteritems():
            for type, betas in type_dict.iteritems():
                m = mean(betas)
                s = std(betas)
                sample_peaks[pos].update({type : (m,s)})
                        
        #print sample_peaks
        self.sample_peaks = sample_peaks

        if self.start == None:
            i = 0
            while self.start == None:
                self.start = self.positions[i]
                i += 1
            print "    New start position:", self.start
        if self.end == None:
            self.end = self.positions[-1]
            print "    New end position:", self.end
         
         
         
        return self.pos_betas_dict, self.sample_peaks


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
        print "   Only %i peaks were found to occur in region." % count
        self.waves = waves
        self.Query['waves'] = waves
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
            filename = "/home/sperez/Documents/svg_temp/" + filename
        elif not get_elements: filename = "test.svg"

        if self.collection == "methylation":
            if color == None: color = "royalblue"
            drawing = methylationplot.MethylationPlot(filename, title, self.sample_peaks,
                                                      self.pos_betas_dict, 
                                                      color, self.start, self.end,
                                                      length, margin, width)
            drawing.build()
        if self.collection == "waves":
            if color == None: color = "indigo"
            drawing = chipseqplot.ChipseqPlot(filename, title, self.waves,
                                              self.start, self.end,
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