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
    classdoc
    '''
    def __init__(self, filename, title, message, sample_peaks, 
                 pos_betas_dict, annotations, color, start, end, 
                 LENGTH, MARGIN, WIDTH):
        '''
        Initialize this object - you need to pass it a mongo object for it to 
        operate on.
        '''
        self.elements = []
        self.title = title
        self.color = color
        self.start = start
        self.end = end
        self.length = LENGTH    # default = 200.0
        self.margin = MARGIN    # default = 20.0
        self.width = WIDTH    # default = 60.0
        self.pos_betas_dict = pos_betas_dict
        self.sample_peaks = sample_peaks
        self.Y = []
        self.annotations = annotations
        self.message = message

        # Default legend coordinates below
        self.axis_x_margin = MARGIN - 5
        self.axis_y_margin = MARGIN - 8

        self.offset_y = None
        self.scale_x = None
        self.scale_y = None

        size = (str(self.length) + "mm" , str(self.width * 1.5) + "mm")
        # create drawing
        self.plot = Drawing(filename, size = size,
                            viewBox = ("0 0 " + str(self.length) + " " + str(self.width + self.margin * 4)),
                            preserveAspectRatio = "xMinYMin meet")
        background = Rect(insert = (0, 0), size = size, fill = "white")
        self.plot.add(background)
        
        if message:
            Message = Text('[ '+message+' ]', insert = ((self.margin + self.length)/3, self.margin+ self.width/2),
                    fill = "black", font_size = 12)
            self.elements.append(Message)
        else:
            self.build()


    def build(self):
        LENGTH, end, start, WIDTH, MARGIN = self.length, self.end, self.start, self.width, self. margin

        for position in self.pos_betas_dict.keys():
            for y, _sample, _sample_type in self.pos_betas_dict[position]:
                self.Y.append(y)
        self.invertby = max(self.Y)
        
        offset_x = start
        self.offset_y = (WIDTH + MARGIN) * 0.8 + MARGIN
        scale_x = LENGTH / (end - start)
        self.scale_x = scale_x
        scale_y = (WIDTH + MARGIN) * 0.8 / max(self.Y)
        self.scale_y = scale_y

        palette.Colors()    # blue, red, green, purple palettes

        for position in self.pos_betas_dict.keys():
            x = round(float(position - offset_x) * scale_x, 2) + MARGIN

            for beta, sample_id, sample_type in self.pos_betas_dict[position]:
                y = round((self.invertby - beta) * scale_y, 2) + MARGIN
                type_color, sample_color = palette.sorter(sample_type, sample_id)
                point = Circle(center = (x, y), r = 0.4, fill = sample_color)
                self.elements.append(point)


            for sample_type in self.sample_peaks[position]:
                type_color, sample_color = palette.sorter(sample_type, None)
                (m, s) = self.sample_peaks[position][sample_type]
                m = round((self.invertby - m) * scale_y, 2) + MARGIN
                s = round(s * scale_y, 3)

                height = 3.0
                if s != 0.0:
                    gaussian_y, gaussian_x = self.makegaussian(s, height)    # reverse output arguments for sideways gaussians
                    gaussian_x = [coord + x - 1 for coord in gaussian_x]
                    gaussian_y = [item + m for item in gaussian_y]
                    d = "M"
                    for i in range(0, len(gaussian_x)):
                        d = d + (" " + str(gaussian_x[i]) + "," + str(gaussian_y[i]))

                    gaussian = (Path(stroke = type_color, stroke_width = 0.1,
                                   stroke_linecap = 'round', stroke_opacity = 0.8,
                                   fill = type_color, fill_opacity = 0.1,
                                   d = d))

                    self.elements.append(gaussian)

        # self.samples_color = samples_color


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
        self.add_sample_labels(self.margin * 3.2 + self.length)
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
        Title = Text(self.title, insert = (self.margin / 3, self.margin / 3),
                fill = "midnightblue", font_size = bigfont)
        self.plot.add(Title)
        self.elements.append(Title)
        
        for axis in get_axis(self.start, self.end, self.length, self.margin, self.width, self.axis_x_margin, self.axis_y_margin):
            self.elements.append(axis)
        
        
        if self.message is '':
            self.add_xtics()
            self.add_ytics()
            self.add_sample_labels(self.margin * 2 + self.length)
            if get_tss:
                for tss in add_tss(self.annotations, self.margin, self.width, self.scale_x, self.start, self.end, self.axis_x_margin, self.axis_y_margin):
                    self.elements.append(tss)
            if get_cpg:
                for cpg in add_cpg(self.annotations, self.margin, self.width, self.scale_x, self.start, self.end, self.axis_x_margin, self.axis_y_margin):
                    self.elements.append(cpg)

    def add_sample_labels(self, x_position):
        ''' TODO: fill in docstring '''
        samples_color = palette.colors_dict()
        if len(samples_color) > 20:
            fontsize = str(float(medfont) - 0.5)
        elif len(samples_color) < 5:
            fontsize = str(float(medfont) + 0.5)
        else: fontsize = medfont

        spacing = 0.1
        y_position = self.margin

        for sample, color in samples_color.iteritems():
            label = Text(sample, insert = (x_position, y_position),
                                            fill = color, font_size = fontsize)
            y_position += float(fontsize) + spacing
            self.elements.append(label)
        return None

    def add_xtics(self):
        ''' TODO: fill in docstring '''
        end, start, WIDTH, MARGIN = self.end, self.start, self. width, self.margin
        offset_x = start
        scale_x = self.scale_x
        scale_tics = 1

        while((scale_tics * 10) < end - start):
            scale_tics *= 10
        xtics = [i for i in range(start, end + 1) if i % (scale_tics) == 0]
        while len(xtics) < 4:
            scale_tics /= 2
            xtics += [i for i in range(start, end + 1) if i % (scale_tics) == 0 and i not in xtics]
        xtics.sort()
        spacing = fabs((MARGIN + (xtics[1] - offset_x) * scale_x) - (MARGIN + (xtics[0] - offset_x) * scale_x)) / 4
        for tic in xtics:
            tic_x = (MARGIN + (tic - offset_x) * scale_x)
            tic_y = WIDTH + MARGIN * 2
            ticmarker = (Text(str(tic), insert = (tic_x, tic_y), fill = "midnightblue", font_size = smallfont))
            ticline = Rect(insert = (tic_x, WIDTH + MARGIN * 2 - 5 - 1), size = (0.1, 2), fill = "midnightblue")
            for i in range (1, 4):
                if tic_x - spacing * i > MARGIN - 5:
                    ticline2 = Rect(insert = (tic_x - spacing * i, WIDTH + MARGIN * 2 - 5 - 1), size = (0.1, 1), fill = "midnightblue")
                    self.elements.append(ticline2)
            self.elements.append(ticline)
            self.elements.append(ticmarker)

    def add_ytics(self):
        ''' TODO: fill in docstring '''
        MARGIN = self.margin
        scale_y, offset_y = self.scale_y, self.offset_y
        ytics = [0, 0.2, 0.4, 0.6, 0.8, 1]
        ytics = [round(offset_y - y * scale_y, 3) for y in ytics]
        spacing = (ytics[0] - ytics[1]) / 2
        for tic in ytics:
            ticline = Rect(insert = (MARGIN - 5 - 1, tic), size = (2, 0.1), fill = "midnightblue")
            ticline2 = Rect(insert = (MARGIN - 5, tic - spacing), size = (1, 0.1), fill = "midnightblue")
            tic_x = MARGIN - 13
            tic_y = tic + 1
            label = str(round((offset_y - tic) / scale_y, 1))
            if len(label) == 1:
                tic_x = tic_x + 3
            if len(label) == 2:
                tic_x = tic_x + 2
            ticmarker = (Text(label, insert = (tic_x, tic_y), fill = "midnightblue", font_size = smallfont))
            self.elements.append(ticline)
            self.elements.append(ticline2)
            self.elements.append(ticmarker)


    def makegaussian(self, stddev, height):
        ''' TODO: fill in docstring '''
        endpts = (sqrt((-2) * stddev * stddev * log(1.0 / height)))
        X = [0]
        X.extend([round(stddev * 2.0 * (i / 9.0) - stddev, 3) for i in range(0, 10)])    # add 10 points  near mean
        X.extend([round(abs(stddev - endpts) * (i / 4.0) + stddev, 3) for i in range(0, 5)])
        X.extend([round(abs(stddev - endpts) * (i / 4.0) - 2.0 * stddev, 3) for i in range(0, 5)])

        X.sort()
        Y = [round(height * exp(-x ** 2 / (2.0 * stddev * stddev)), 3) for x in X]
        return X, Y
