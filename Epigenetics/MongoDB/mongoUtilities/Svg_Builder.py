'''
Created on 2013-05-23

@author: sperez, apfejes

'''
from Illustration import SVGPlot

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
            get_minheight = False,
            get_tss = False,
            get_cpg = False,
            show_points = False,
            show_dist = False):
        ''' Plots the data using different SVG modules in Epigenetics/Illustrations
            Saves the plot as an .svg file or a svg string for webserver rendering
        '''

        # TODO: Set up mechanism for writing out to file
#         if filename:
#             if filename[-4:len(filename)] != '.svg':
#                 filename += '.svg'
#             filename = directory_for_svgs + filename

        self.drawing = SVGPlot.Plot()
        self.drawing.set_properties(filename, title, self.start, self.end, width, height)

        if types_index:    # if types index, assume types and sample index both need to be restored to preserve colours.
            self.drawing.set_sample_index(types_index, sample_index)

        # #NOTE: Peaks must go before methylation, otherwise white boxes cover methylation labels.
        if self.peaks:    # information about waves is already pushed by MEW.
            self.drawing.build_chipseq(self.error_message, self.waves)
            if self.waves:
                self.drawing.add_ytics_chipseq()

        if self.methylation:
            self.drawing.build_methylation(self.error_message, self.pos_betas_dict, self.sample_peaks, show_points, show_dist)
            self.drawing.add_ytics_methylation()




        # TODO: Insert error handling here, if methylation and no methylation data, drop out
        # TODO: Insert error handling here, if chipseq and no chipseq data, drop out
        # TODO: Insert error handling here, if both and no data, drop out


        sampleindex = self.drawing.get_sample_index()
        typesindex = self.drawing.get_types_index()

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

