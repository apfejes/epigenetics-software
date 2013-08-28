'''
Created on 2013-06-10

@author: sperez
'''

from svgwrite.shapes import Rect, Circle
from svgwrite.text import Text
from svgwrite.drawing import Drawing
from svgwrite.path import Path
from math import fabs, exp, sqrt, log
import Color_Palette
palette = Color_Palette.ColorPalette()

from PlotUtilities import add_cpg, add_tss, get_axis, bigfont, medfont, smallfont

class MethylationPlot(object):
    '''
    Called by a MongoCurious object to plot methylation data.
    '''

    DOT_RADIUS = 2
    DISTR_HT = 12.0
    DISTR_STROKE = 0.5
    BOTTOM_MARGIN = 120    # 120 pixels
    RIGHT_MARGIN = 70
    MARGIN = 30


    def __init__(self, filename, title, message, sample_peaks,
                 pos_betas_dict, annotations, color, start, end,
                 width, height, show_points, show_peaks):
        '''
        Initialize this object - you need to pass it a mongo object for it to 
        operate on.
        '''
        self.elements = []
        self.title = title
        self.color = color
        self.start = start
        self.end = end
        self.width = width    # default = 200.0

        self.height = height    # default = 60.0
        self.annotations = annotations
        self.message = message

        self.dimension_y = self.height - self.MARGIN - self.BOTTOM_MARGIN    # this is the size of the y field
        self.dimension_x = self.width - self.MARGIN - self.RIGHT_MARGIN
        self.scale_x = float(self.dimension_x) / (self.end - self.start)    # this is a scaling variable

        size = (str(self.width) + "px" , str(self.height) + "px")
        # create drawing
        self.plot = Drawing(filename, size = size
                            # , viewBox = ("0 0 " + str(self.height) + " " + str(self.width + (self.margin * 2)))
                            # , preserveAspectRatio = "xMinYMin meet"
                            )
        background = Rect(insert = (0, 0), size = size, fill = "white")
        self.plot.add(background)

        if message:
            Message = Text('[ ' + message + ' ]', insert = (float(self.width) / 3.0, float(self.height) / 2.0),
                    fill = "black", font_size = bigfont * 2)
            self.elements.append(Message)
        else:
            self.build(pos_betas_dict, sample_peaks, show_points, show_peaks)


    def build(self, pos_betas_dict, sample_peaks, show_points, show_peaks):
        '''TODO: missing docstring'''
        all_y = []
        for position in pos_betas_dict.keys():
            for y, _sample, _sample_type in pos_betas_dict[position]:
                all_y.append(y)
        # self.max_y_value = max(all_y)    # (max y value - value /y height) + margin gives you position
            # / self.max_y_value
        palette.Colors()    # blue, red, green, purple palettes

        for position in pos_betas_dict.keys():
            x = round(float(position - self.start) * self.scale_x, 2) + self.MARGIN

            if show_points:
                for beta, sample_id, sample_type in pos_betas_dict[position]:
                    y = round((1 - beta) * self.dimension_y, 2) + self.MARGIN
                    type_color, sample_color = palette.sorter(sample_type, sample_id)
                    point = Circle(center = (x, y), r = self.DOT_RADIUS, fill = sample_color)
                    self.elements.append(point)

            if show_peaks:
                for sample_type in sample_peaks[position]:
                    type_color, sample_color = palette.sorter(sample_type, None)
                    (m, s) = sample_peaks[position][sample_type]
                    m = round((1 - m) * self.dimension_y, 2) + self.MARGIN
                    s = round(s * self.dimension_y, 3)


                    if s != 0.0:
                        gaussian_y, gaussian_x = self.makegaussian(s, self.DISTR_HT)    # reverse output arguments for sideways gaussians
                        gaussian_x = [coord + x - 1 for coord in gaussian_x]
                        gaussian_y = [item + m for item in gaussian_y]
                        d = "M"
                        for i in range(0, len(gaussian_x)):
                            d = d + (" " + str(gaussian_x[i]) + "," + str(gaussian_y[i]))

                        gaussian = (Path(stroke = type_color,
                                         stroke_width = self.DISTR_STROKE,
                                         stroke_linecap = 'round',
                                         stroke_opacity = 0.8,
                                         fill = type_color,
                                         fill_opacity = 0.1,
                                       d = d))

                        self.elements.append(gaussian)


    def save(self):
        ''' TODO: fill in docstring '''
        for element in self.elements:
            self.plot.add(element)
        self.plot.save()

    def to_string(self):
        ''' TODO: fill in docstring '''
        for element in self.elements:
            self.plot.add(element)
        z = self.plot.tostring()
        self.plot = None
        return z

    def get_xml(self):
        ''' TODO: fill in docstring '''
        strings = ""
        for element in self.elements:
            strings += (element.get_xml().decode('utf-8'))
        return strings

    def get_elements(self):
        ''' TODO: fill in docstring '''
        self.add_sample_labels(self.MARGIN * 3.2 + self.width)
        z = self.elements
        self.elements = None
        return z

    def add_data(self, elements = None):
        ''' TODO: fill in docstring '''
        elements_to_add = elements
        for element in elements_to_add:
            self.plot.add(element)
        print "% i svg elements have been added to the current svg object." % len(elements)

    def add_legends(self, get_tss, get_cpg):
        ''' Add annotations, title, axis, tic marks and labels '''
        if self.title is None:
            self.title = "Methylation PLot"
        Title = Text(self.title, insert = (bigfont + ((float(self.MARGIN) - bigfont) / 3),
                                           bigfont + ((float(self.MARGIN) - bigfont) / 3)),
                                           fill = "midnightblue", font_size = bigfont)
        self.elements.append(Title)

        for axis in get_axis(self.start, self.end, self.width, self.MARGIN, self.height, self.BOTTOM_MARGIN, self.RIGHT_MARGIN):
            self.elements.append(axis)

        if self.message is '':
            self.add_xtics()
            self.add_ytics()
            self.add_sample_labels(self.width - self.RIGHT_MARGIN + 20)
            if get_tss:
                for tss in add_tss(self.annotations, self.MARGIN, self.height, self.scale_x, self.start, self.end, self.BOTTOM_MARGIN):
                    self.elements.append(tss)
            if get_cpg:
                for cpg in add_cpg(self.annotations, self.MARGIN, self.height, self.scale_x, self.start, self.end, self.BOTTOM_MARGIN):
                    self.elements.append(cpg)

    def add_sample_labels(self, x_position):
        ''' TODO: fill in docstring '''
        samples_color = palette.colors_dict()
        if len(samples_color) > 20:
            fontsize = str(float(medfont) - 0.5)
        elif len(samples_color) < 5:
            fontsize = str(float(medfont) + 0.5)
        else: fontsize = medfont

        spacing = 1
        y_position = self.MARGIN

        for sample, color in samples_color.iteritems():
            label = Text(sample, insert = (x_position, y_position),
                                            fill = color, font_size = fontsize)
            y_position += float(fontsize) + spacing
            self.elements.append(label)
        return None

    def add_xtics(self):
        ''' TODO: fill in docstring '''
        scale_tics = 1

        while((scale_tics * 10) < self.end - self.start):
            scale_tics *= 10
        # TODO: fix the line below.
        xtics = [i for i in range(self.start, self.end + 1) if i % (scale_tics) == 0]
        while len(xtics) < 4:
            scale_tics /= 2
            # TODO: fix the line below.
            xtics += [i for i in range(self.start, self.end + 1) if i % (scale_tics) == 0 and i not in xtics]
        xtics.sort()
        spacing = fabs((self.MARGIN + (xtics[1] - self.start) * self.scale_x) - (self.MARGIN + (xtics[0] - self.start) * self.scale_x)) / 4
        for tic in xtics:
            tic_x = (self.MARGIN + (tic - self.start) * self.scale_x)
            tic_y = self.height - self.BOTTOM_MARGIN + smallfont * 1.5
            ticmarker = (Text(str(tic), insert = (tic_x, tic_y), fill = "midnightblue", font_size = smallfont))
            ticline = Rect(insert = (tic_x, self.height - self.BOTTOM_MARGIN - 2), size = (1, 5), fill = "midnightblue")
            for i in range (1, 4):
                if tic_x - spacing * i > self.MARGIN - 5:
                    ticline2 = Rect(insert = (tic_x - spacing * i, self.height - self.BOTTOM_MARGIN - 2), size = (1, 2), fill = "midnightblue")
                    self.elements.append(ticline2)
            self.elements.append(ticline)
            self.elements.append(ticmarker)

    def add_ytics(self):
        ''' TODO: fill in docstring '''
        labels = [0, 0.2, 0.4, 0.6, 0.8, 1]
        ytics = [round((self.MARGIN + self.dimension_y) - (y * self.dimension_y), 3) for y in labels]
        spacing = (ytics[0] - ytics[1]) / 2
        for tic, label in zip(ytics, labels):
            ticline = Rect(insert = (self.MARGIN - 2, tic), size = (5, 1), fill = "midnightblue")
            if tic - spacing > self.MARGIN:
                ticline2 = Rect(insert = (self.MARGIN - 2, tic - spacing), size = (2, 1), fill = "midnightblue")
                self.elements.append(ticline2)
            tic_x = self.MARGIN - smallfont * 2
            tic_y = tic + 1
            if len(str(label)) == 1:
                tic_x = tic_x + 3
            if len(str(label)) == 2:
                tic_x = tic_x + 2
            ticmarker = (Text(label, insert = (tic_x, tic_y), fill = "midnightblue", font_size = smallfont))
            self.elements.append(ticline)
            self.elements.append(ticline2)
            self.elements.append(ticmarker)

    @staticmethod
    def makegaussian(stddev, innerheight):
        ''' TODO: fill in docstring '''
        endpts = (sqrt((-2) * stddev * stddev * log(1.0 / innerheight)))
        X = [0]
        X.extend([round(stddev * 2.0 * (i / 9.0) - stddev, 3) for i in range(0, 10)])    # add 10 points  near mean
        X.extend([round(abs(stddev - endpts) * (i / 4.0) + stddev, 3) for i in range(0, 5)])
        X.extend([round(abs(stddev - endpts) * (i / 4.0) - 2.0 * stddev, 3) for i in range(0, 5)])

        X.sort()
        Y = [round(innerheight * exp(-x ** 2 / (2.0 * stddev * stddev)), 3) for x in X]
        return X, Y
