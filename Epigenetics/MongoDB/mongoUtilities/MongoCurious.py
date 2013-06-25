'''
Created on 2013-05-23

@author: sperez

'''
from time import time
import os, sys
from numpy import log, mean
from math import sqrt

_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)

sys.path.insert(0, _root_dir + os.sep + "MongoDB" + os.sep + "mongoUtilities")
import Mongo_Connector
import MongoQuery
sys.path.insert(0, _cur_dir + os.sep + "Illustration")
import Illustration.ChipseqPlot as chipseqplot
import Illustration.MethylationPlot as methylationplot


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
        if chromosome == None:
            raise ValueError("Please specificy a chromosome.")
        if isinstance(chromosome, basestring):
            Query['chromosome'] = chromosome
            self.chromosome = chromosome
        elif isinstance(chromosome, int):
                Query['chromosome'] = 'chr' + str(chromosome)
                self.chromosome = chromosome
        Query['start'] = int(start)
        self.start = int(start)
        Query['end'] = int(end)
        self.end = int(end)
        Query['sample label'] = sample_label
        self.sample_label = sample_label
        Query['sample type'] = sample_type
        self.sample_type = sample_type
        Query['sample id'] = sample_id
        self.sample_id = sample_id
        if self.project:
            self.sample_groups = self.creategroups()
            Query['sample groups'] = self.sample_groups
        self.Query = Query
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


    def finddocs(self):
        '''Finds probes or documents corresponding to query'''
        #self.mongo.ensure_index(self.collection, 'start_position')    # for speed? to be tested...

        # Preparing the different parameters of the query depending on the collection chosen
        if self.collection == "methylation":
            query_chr, query_start, query_end, query_samplabel = {}, {}, {}, {}
            if self.chromosome != None: query_chr = {'chr':self.chromosome}
            if self.end != None: query_start = {"start_position":{"$lte":self.end}}
            if self.start != None: query_end = {"end_position":{"$gte":self.start}}
            if self.sample_label != None: query_samplabel = {"sample_label":self.sample_label}
            query = dict(query_chr.items() + query_start.items() + query_end.items() + query_samplabel.items())
            return_chr = {'_id': False, 'beta_value': True,
                          'start_position': True, 'end_position': True,
                          'sample_label': True}
            print "\n Conducting query: "
            print "   From the database '{0}', and collection '{1}', ".format(self.database, self.collection)
            print "   Find(", query, ")"
            # Get probes corresponding to query and sort by starting positions for beta value binning
            docs = self.mongo.find(self.collection, query, return_chr).sort('start_position', 1)

        if self.collection == "waves":
            self.mongo.ensure_index(self.collection, 'pos')
            query_chr, query_pos, = {}, {}
            if self.chromosome != None: query_chr = {'chr':self.chromosome}
            if self.start != None and self.end != None:
                extension = 500    # extend the region of query to catch peaks with tails in the region
                query_pos = {"pos":{"$lte":self.end + extension, "$gte":self.start - extension}}
            query = dict(query_chr.items() + query_pos.items())
            return_chr = {'_id': False, 'pos': True,
                          'height': True, 'stddev': True,
                          'sample_id': True}
            print "\n Conducting query: "
            print "   From the database '{0}', and collection '{1}', ".format(self.database, self.collection)
            print "   Find(", query, ")"
            # Get documents corresponding to query and sort by inverse peak height for plotting purposes
            docs = self.mongo.find(self.collection, query, return_chr).sort('height', -1)

        if docs.count() == 0:
            print("    WARNING: The following query return zero probes or documents!")
            print "    ---> Find(", query, ")"
            print "     use the checkquery() method to validate the inputs of your query."
            sys.exit()

        print " Found %i probes or documents." % docs.count()
        self.docs = docs
        self.count = self.docs.count()
        self.Query['cursor'] = self.docs
        return None


    def creategroups(self):
        '''
        Separate samples into 'groups' according to a particular feature and sample_type like disease
        or control.
        samplegroup is a list of sample labels with the desired sample_type of that feature.
        '''
        print "    Creating sample groups..."
        if self.project == "down":
            if self.sample_type not in ["Control", "DS"]: self.sample_type = str(raw_input(
            				"Please specify a sample type: \"Control\" or \"DS\"?"))
            feature = 'Sample Group'
            samplegroup = self.sample_dict(project = self.project, feature = feature)[self.sample_type]
        if self.project == "kollman":
            if self.sample_type not in ["unstimulated", "listeria"]: self.sample_type = str(raw_input(
            				"Please specify a sample type: \"unstimulated\" or \"listeria\"?"))
            feature = 'stimulation'
            samplegroup = self.sample_dict(project = self.project, feature = feature)[self.sample_type]
        if self.project == "All":
            if self.sample_type != "control" or self.sample_type != None:
                print "The sample type \"", self.sample_type, "\" is invalid."
                self.sample_type = str(raw_input("Please specify a sample type: \"control\" or \"disease\"?"))
            if self.sample_type == "control" or self.sample_type == None:
                samplegroup = self.sample_dict(project = "kollman", feature = "stimulation")["unstimulated"]
                samplegroup.append(self.sample_dict(project = "down", feature = "Sample Group")["Control"])
                samplegroup.append(self.sample_dict(project = "kollman", feature = "stimulation",
                					nottype = ["unstimulated", "listeria"]))
                samplegroup.append(self.sample_dict(project = "down", feature = "Sample Group",
                					nottype = ["Control", "DS"]))
            if self.sample_type == "disease":
                samplegroup = self.sample_dict(project = "kollman", feature = "stimulation")["listeria"]
                samplegroup.append(self.sample_dict(project = "down", feature = "Sample Group")["DS"])

        print "    The sample labels with sample type", self.sample_type, " are:", samplegroup
        return samplegroup

    def sample_dict(self, project, feature, nottype = None):
        '''
        For a particular feature (for example, disease in Down Syndrome experiments) return a dictionary
        structured as {sample label: sample_type} where sample_type is "control" or "diseased
        '''

        print "    Appending labels for project", project, "and", feature
        self.mongo.ensure_index("samples", project)    # For speed
        self.mongo.ensure_index("samples", feature)

        if nottype != None:
            add_query = {feature:{"$ne":nottype[0], "$ne":nottype[1]}}
            findQuery = dict({'project': project}.items() + add_query.items())
        else: findQuery = {'project': project}
        returnQuery = {feature: True, '_id': False, 'sample_label': True}

        samples = self.mongo.find("samples",
                             findQuery, returnQuery).sort(feature, 1)
        sample_groups = {}
        sample_labels_list = []
        previous_group = None
        count = 0
        for doc in samples:
            if (doc[feature] != previous_group) and (count > 0):
                sample_groups[previous_group] = sample_labels_list
                sample_labels_list = []
            sample_labels_list.append(doc['sample_label'])
            previous_group = doc[feature]
            count += 1
        sample_groups[previous_group] = sample_labels_list    # Do once more after exiting loop
        print sample_groups
        return sample_groups

    def collectbetas(self,
                     separate_samples = False,
                     window_size = 1):
        '''Collects and bins methylation data'''

        # Bin the beta values and collect average positions
        position_dic = {}
        betasamp_list = []
        count = 0
        for doc in self.docs:
            if count == 0:
                prev_start_pos = doc['start_position']
            if count != 0:
                if (doc['start_position'] - prev_start_pos) > window_size:
                    avg_position = (doc['start_position'] + prev_start_pos) / 2
                    position_dic[avg_position] = betasamp_list
                    betasamp_list = []
                    prev_start_pos = doc['start_position']
            betasamp_list.append((doc['beta_value'], doc['sample_label']))
            count += 1
        avg_position = (doc['start_position'] + prev_start_pos) / 2
        position_dic[avg_position] = betasamp_list

        print '    %s probes\' beta values were extracted and binned.' % count

        
        sample_ids = []
        x_position = []
        y_avg = []
        for pos, tup_list in sorted(position_dic.iteritems()):
            beta_values = []
            for beta, samp in tup_list:
                if separate_samples:
                    if self.sample_type == None or samp in self.sample_groups:
                        x_position.append(pos)
                        y_avg.append(beta)
                        sample_ids.append(samp)
                else:
                    if self.sample_type == None or samp in self.sample_groups:
                        beta_values.append(beta)
                    else: continue
                    data_avg = mean(beta_values)
                    x_position.append(pos)
                    y_avg.append(data_avg)

        print "    %i beta values collected" % len(x_position)
        self.positions = x_position
        self.betas = y_avg
        self.sample_ids = sample_ids

        if self.start == None:
            i = 0
            while self.start == None:
                self.start = self.positions[i]
                i += 1
            print "    New start position:", self.start
        if self.end == None:
            self.end = self.positions[-1]
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
            # append all peaks with a center in the region
            if self.start <= pos <= self.end:
                waves.append((pos, height, stddev, sample_id))
                count += 1
            else:
                dist_to_region = min(abs(pos - self.end), abs(self.start - pos))
                dist_from_peak_to_tail = sqrt((-2) * stddev * stddev * log(tail / height))
                if dist_from_peak_to_tail - dist_to_region >= 0:
                    waves.append((pos, height, stddev, sample_id))
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
            filename = "/home/sperez/Documents/svg_temp/" + filename
        elif not get_elements: filename = "test.svg"

        if self.collection == "methylation":
            if color == None: color = "royalblue"
            drawing = methylationplot.MethylationPlot(filename, title,
                                                      self.positions, self.betas,
                                                      self.sample_ids, color,
                                                      self.start, self.end,
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
        elif get_elements:
            z = drawing.get_elements()
            print " Returning %i svg elements" % len(z)
        elif filename and not to_string and not get_elements:
            print " Making svg file \"%s\"\n" % filename
            drawing.add_legends()
            z = drawing
            z.save()
        else:
            print "No filename specified. Returning the SVG object with legends"
            drawing.add_legends()
            z = drawing
        drawing = None
        return z


