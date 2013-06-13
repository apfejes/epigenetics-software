from svgwrite.shapes import Rect
from svgwrite.shapes import Line
# from svgwrite.shapes import Circle
from svgwrite.text import Text
from svgwrite.drawing import Drawing


# We get coordinates from querying ensembl normally but that takes time
# so here is the coordinates of the exons for the huntington gene:
# from query_ensembl import coordinates
# from query_ensembl import name, location

class Histogram(object):
    '''
    classdocs
    '''
    def __init__(self, filename, bins, **kwargs):
        '''
        Initialize this object - you need to pass it a mongo object for it to 
        operate on.
        '''
        self.filename = filename
        self.bins = bins
        self.data_max = 0
        self.data_min = 0
        self.x_min = 0

        if 'x_max' in kwargs:
            self.x_max = kwargs['x_max']
        else:
            self.x_max = 0
        if 'x_min' in kwargs:
            self.x_min = kwargs['x_min']
        else:
            self.x_min = 0
        if 'gap' in kwargs:
            self.gap = kwargs['gap']
        else:
            self.gap = 5
        if 'height' in kwargs:
            self.height = kwargs['height']
        else:
            self.height = 600
        if 'width' in kwargs:
            self.width = kwargs['width']
        else:
            self.width = 1200
        if 'debug' in kwargs:
            self.debug = kwargs['debug']
        else:
            self.debug = True
        if 'margin_top' in kwargs:
            self.margin_top = kwargs['margin_top']
        else:
            self.margin_top = 20
        if 'margin_bottom' in kwargs:
            self.margin_bottom = kwargs['margin_bottom']
        else:
            self.margin_bottom = 20
        if 'margin_left' in kwargs:
            self.margin_left = kwargs['margin_left']
        else:
            self.margin_left = 20
        if 'margin_right' in kwargs:
            self.margin_right = kwargs['margin_right']
        else:
            self.margin_right = 20
        self.data = None
        self.binned_data = None

        # start drawing object
        self.plot = Drawing(self.filename, debug = self.debug,
                            size = (self.width + self.margin_left + self.margin_right,
                                    self.height + self.margin_top + self.margin_bottom),
                            # viewBox = ("0 0 " + str(float(length) + 10) + " " + str(float(width) + 10)),
                            preserveAspectRatio = "xMinYMin meet")    # , size=('200mm', '150mm'), viewBox=('0 0 200 150'))
        self.plot.add(Line(start = (self.margin_left - 4, self.margin_top), \
                           end = (self.margin_left - 4, self.margin_top + self.height),
                           stroke_width = 0.5, stroke = "black"))
        self.plot.add(Line(start = (self.margin_left, self.margin_top + self.height + 4),
                           end = (self.margin_left + self.width, self.margin_top + self.height + 4),
                           stroke_width = 0.5, stroke = "black"))

    def add_data(self, x):
        self.data = x

    def bin_data(self):
        self.binned_data = {}
        for i in range(self.bins + 1):
            self.binned_data[i] = 0
        if self.x_max == 0 and self.x_min == 0 :
            self.x_min = self.data[0]
            for x in self.data:
                if x > self.x_max:
                    self.x_max = x
                if x < self.x_min:
                    self.x_min = x
        # print "self.x_max = %f" % (self.x_max)
        bin_size = (float(self.x_max) - self.x_min) / self.bins
        print "bin_size: %f" % (bin_size)
        for x in self.data:
            # print "x: %i - bin_size: %f" % (x, bin_size)
            # print "x//bin_size = %f int() = %i" % (x // bin_size, int(x // bin_size))
            k = 0
            if x > self.x_max:
                k = self.bins + 1
            else:
                k = int(x // bin_size)
            if k > self.bins:
                k = self.bins
            self.binned_data[k] += 1    # floored division.
            if self.binned_data[k] > self.data_max:
                self.data_max = self.binned_data[k]
        for i in range(self.bins + 1):
            print "%i %i" % (i, self.binned_data[i])

    def x_to_printx(self, x):
        return self.margin_left + ((float(x) / self.x_max) * self.width)


    def build(self):
        bin_width = (self.width - ((self.bins + 1) * self.gap)) // self.bins    # floored division
        for i in range(self.bins):
            self.plot.add(Rect(insert = (self.margin_left + self.gap + (i * (bin_width + self.gap)),
                                       (self.margin_top + self.height) - ((float(self.binned_data[i]) / self.data_max) * self.height)),
                               size = (bin_width, ((float(self.binned_data[i]) / self.data_max) * self.height)),
                               fill = "red"))
            self.plot.add(Text(i , insert = (self.margin_left + self.gap + (i * (bin_width + self.gap)), self.height + self.margin_top + 20), fill = "midnightblue", font_size = "15"))
        self.data = None


    def save(self):
        self.plot.save()
        self.plot = None

    def to_string(self):
        z = self.plot.tostring()
        self.plot = None
        return z

