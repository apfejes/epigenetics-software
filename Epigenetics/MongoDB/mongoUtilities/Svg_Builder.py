'''
Created on 2013-05-23

@author: sperez, apfejes

'''

import ChipseqPlot as chipseqplot
import MethylationPlot as methylationplot


directory_for_svgs = "/home/sperez/Documents/svg_temp/"

class Svg_Builder():
    '''A class plot SVGs'''

    def __init__(self, methylation, peaks, start, end):
        '''Performs the connection to the Mongo database.'''

        self.pos_betas_dict = None    # initialize self parameters
        self.collection = None
        # self.chromosome = None
        self.sample_peaks = None
        self.end = end
        self.start = start
        self.waves = None
        self.annotations = None
        self.error_message = ''
        self.drawing = None
        self.methylation = methylation
        self.peaks = peaks



    def svg(self,

            types_index = None,
            sample_index = None,
            filename = None,
            title = None,
            color = None,
            to_string = False,
            get_elements = False,
            height = 200.0,
            width = 60.0,
            get_tss = False,
            get_cpg = False,
            show_points = False,
            show_dist = False):
        ''' Plots the data using different SVG modules in Epigenetics/Illustrations
            Saves the plot as an .svg file or a svg string for webserver rendering
        '''
        if filename:
            if filename[-4:len(filename)] != '.svg':
                filename += '.svg'
            filename = directory_for_svgs + filename



        if self.methylation:
            if self.drawing == None:
                self.drawing = methylationplot.MethylationPlot()
            if sample_index:
                print "Setting sample index to %s" % (sample_index)
                print "Setting types index to %s" % (types_index)
                self.drawing.set_sample_index(types_index, sample_index)
            else:
                print "Not setting sample or types index."
            self.drawing.set_properties(filename, title, color, self.start, self.end, width, height)
            self.drawing.build(self.error_message, self.pos_betas_dict, self.sample_peaks, show_points, show_dist)
            sampleindex = self.drawing.get_sample_index()
            typesindex = self.drawing.get_types_index()

                # self.drawing = methylationplot.MethylationPlot(filename, title, self.error_message, self.sample_peaks,
                #                                      self.pos_betas_dict, self.annotations,
                #                                      color, self.start, self.end, width,
                #                                      height, show_points, show_peaks)

        if self.peaks:
            self.drawing = chipseqplot.ChipseqPlot(filename, title, self.error_message, self.waves, self.start,
                                              self.end, self.annotations, width,
                                              height)
            # TODO: SAMPLE NAMES/type names MUST BE RETRIEVED HERE. - mirror code above

        if get_elements:
            self.drawing.add_sample_labels()
            z = self.drawing.get_elements()
            print " Returning %i svg elements" % len(z)
            return z, sampleindex, typesindex


        if (self.error_message == ''):
            self.drawing.add_legends(get_tss, get_cpg, self.annotations)
        if to_string:
            print " Returning svg as a unicode string"
            z = self.drawing.to_string()
        elif filename and not to_string and not get_elements:
            print " Making svg file \"%s\"\n" % filename
            z = self.drawing
            z.save()
        else:
            print "No filename specified. Returning the SVG object without legends"
            z = self.drawing
            self.drawing = None
        return z, sampleindex, typesindex

