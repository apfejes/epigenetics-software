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
        self.probes_by_pos = None    # assigned by MEW.getprobes()
        self.probe_details = None    # assigned by MEW.getprobes()

    def svg(self,
            types_index=None,
            sample_index=None,
            filename=None,
            title=None,
            to_string=False,
            get_elements=False,
            height=200.0,
            width=60.0,
            get_cpg=False,
            show_points=False,
            show_dist=False,
            show_genes=True,
            # whether to show the genes on the bottom of the illustration.
            show_groups=None,
            # If you want to show only a subset of available groups, give the list here.
            bigger_dists=False,
            trace=False,
            genes=None):
        # Plots the data using different SVG modules in Epigenetics/Illustrations
        # Saves the plot as an SVG string for webserver rendering

        self.drawing = SVGPlot.Plot()
        self.drawing.set_properties(filename, title, self.start, self.end,
                                    width, height)

        if types_index:     # if types index, assume types and sample index both
                            # need to be restored to preserve colours.
            self.drawing.set_sample_index(types_index, sample_index)

        # NOTE: Peaks must go before methylation,
        # otherwise white boxes cover methylation labels.
        if self.peaks:    # information about waves is already pushed by MEW.
            self.drawing.build_chipseq(self.error_message, self.waves, trace)
            if self.waves:
                self.drawing.add_ytics_chipseq()

        if self.methylation:
            self.drawing.build_methylation(self.error_message,
                                           self.pos_betas_dict,
                                           self.sample_peaks,
                                           show_points, show_dist, show_groups,
                                           self.probes_by_pos,
                                           self.probe_details, bigger_dists,
                                           trace)
            self.drawing.add_ytics_methylation()

        if genes and show_genes:
            self.drawing.draw_genes(genes)

        sampleindex = self.drawing.get_sample_index()
        typesindex = self.drawing.get_types_index()

        if get_elements:
            self.drawing.add_sample_labels()
            z = self.drawing.get_elements()
            print " Returning %i svg elements" % len(z)
            return z, sampleindex, typesindex

        if self.error_message == '':
            self.drawing.add_legends(get_cpg, self.annotations)
        if to_string:
            print " Returning svg as a unicode string"
            z = self.drawing.to_string()
        elif filename and not to_string and not get_elements:
            print " Making svg file \"%s\"\n" % filename
            z = self.drawing
            z.save()
        else:
            print "No filename specified. Returning the SVG object " \
                  "without legends"
            z = self.drawing
            self.drawing = None
        return z, sampleindex, typesindex
