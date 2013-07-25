'''
Created on 2013-06-10

@author: sperez
'''

from svgwrite.shapes import Rect, Circle
from svgwrite.text import Text
from svgwrite.drawing import Drawing
from svgwrite.path import Path
from math import fabs, exp, sqrt, log
from numpy import mean
import Color_Palette 
palette = Color_Palette.ColorPalette()

class MethylationPlot(object):
    '''
    classdocs
    '''
    def __init__(self, filename, title, sample_peaks, pos_betas_dict, color, start, end, length, margin, width):
        '''
        Initialize this object - you need to pass it a mongo object for it to 
        operate on.
        '''
        self.elements = []
        self.title = title
        self.color = color
        self.start = start
        self.end = end
        self.length = length    # default = 200.0
        self.margin = margin    # default = 20.0
        self.width = width    # default = 60.0
        self.pos_betas_dict = pos_betas_dict
        self.sample_peaks = sample_peaks
        self.Y = []
        
        for position in self.pos_betas_dict.keys():
            for y, sample, sample_type in pos_betas_dict[position]:
                self.Y.append(y)
        self.invertby = max(self.Y)
        
        # create drawing
        self.plot = Drawing(filename,
                        size = (str(self.length) + "mm" , str(self.width * 1.5) + "mm"),
                        viewBox = ("0 0 " + str(self.length) + " " + str(self.width + self.margin * 4)),
                        preserveAspectRatio = "xMinYMin meet")


    def build(self):
        length, end, start, width, margin, invertby = self.length, self.end, self.start, self.width, self. margin, self.invertby

        offset_x = start
        self.offset_y = (width + margin) * 0.8 + margin
        scale_x = length / (end - start)
        self.scale_x = scale_x
        scale_y = (width + margin) * 0.8 / max(self.Y)
        self.scale_y = scale_y
        
        colors, color_wheel = palette.Colors()       #blue, red, green, purple palettes

        for position in self.pos_betas_dict.keys():
            x = round(float(position - offset_x) * scale_x, 2) + margin
            
            for beta, sample_id, sample_type in self.pos_betas_dict[position]:
                y = round((invertby - beta) * scale_y, 2) + margin
                type_color, sample_color = palette.sorter(sample_type, sample_id)
                point = Circle(center = (x, y), r = 0.3, fill = sample_color)
                self.elements.append(point)
            
            for sample_type in self.sample_peaks[position]:
                type_color, sample_color = palette.sorter(sample_type, sample_id)
                (m,s) = self.sample_peaks[position][sample_type]
                m = round((invertby - m) * scale_y, 2) +margin
                s = round(s * scale_y,3)
                #point = Circle(center = (x, m), r = 0.6, fill = 'black')
                self.elements.append(point)
                
                height = 3.0
                if s!= 0.0:
                    gaussian_y, gaussian_x = self.makegaussian(m, s, height) #reverse output arguments for sideways gaussians
                    gaussian_x = [coord + x -1 for coord in gaussian_x]
                    gaussian_y = [item + m for item in gaussian_y]
                    #print "hello", y, gaussian_y
                    #offset_x = max(Y)
                    #Y = [(coord-offset_x)*0.1+offset_x for coord in Y]
                    d = "M"
                    for i in range(0, len(gaussian_x)):
                        d = d + (" " + str(gaussian_x[i]) + "," + str(gaussian_y[i]))
         
                    gaussian = (Path(stroke = type_color, stroke_width = 0.1,
                                   stroke_linecap = 'round', stroke_opacity = 0.8,
                                   fill = type_color, fill_opacity = 0.1, 
                                   d = d))
         
                    self.elements.append(gaussian)
                    
        #self.samples_color = samples_color

    def save(self):
        for element in self.elements:
            self.plot.add(element)
        self.plot.save()

    def to_string(self):
        for element in self.elements:
            self.plot.add(element)
        z = self.plot.tostring()
        self.plot = None
        return z

    def get_elements(self):
        self.add_sample_labels(self.margin*3.2 + self.length)
        z = self.elements
        self.elements = None
        return z

    def add_data(self, elements = None):
        elements_to_add = elements
        if not isinstance(elements_to_add, list):
            raise ValueError("Data to add to plot should be stored in a list, not a {}".format(type(elements)))
        for element in elements_to_add:
            self.plot.add(element)
        print "% i svg elements have been added to the current svg object." % len(elements)

    def add_legends(self):
        ''' Add title, axis, tic marks and labels '''
        if self.title == None:
            self.title = "Methylation PLot"
        Title = Text(self.title, insert = (self.margin, self.margin - 10.0),
                fill = "midnightblue", font_size = "5")
        self.plot.add(Title)
        self.elements.append(Title)
        self.add_xtics()
        self.add_ytics()
        self.add_axis()
        self.add_sample_labels(self.margin*2 + self.length)

    def add_sample_labels(self,x_position):
        samples_color = palette.colors_dict()
        if len(samples_color)>20: 
            fontsize = '2.5'
        elif len(samples_color)<5: 
            fontsize = '3.5'
        else: fontsize = '3'
        
        spacing = 0.1
        y_position = self.margin
        
        for sample, color in samples_color.iteritems():
            label = Text(sample, insert = (x_position, y_position),
                                            fill = color, font_size = fontsize)
            y_position += float(fontsize)+spacing
            self.elements.append(label)
        return None
    
    def add_xtics(self):
        end, start, width, margin = self.end, self.start, self. width, self.margin
        offset_x = start
        scale_x = self.scale_x
        scale_tics = 1;

        while((scale_tics * 10) < end - start):
            scale_tics *= 10;
        xtics = [i for i in range(start, end + 1) if i % (scale_tics) == 0]
        while len(xtics) < 4:
            scale_tics /= 2
            xtics += [i for i in range(start, end + 1) if i % (scale_tics) == 0 and i not in xtics]
        xtics.sort()
        spacing = fabs((margin + (xtics[1] - offset_x) * scale_x) - (margin + (xtics[0] - offset_x) * scale_x)) / 4
        for tic in xtics:
            tic_x = (margin + (tic - offset_x) * scale_x)
            tic_y = width + margin * 2
            ticmarker = (Text(str(tic), insert = (tic_x, tic_y), fill = "midnightblue", font_size = "3"))
            ticline = Rect(insert = (tic_x, width + margin * 2 - 5 - 1), size = (0.1, 2), fill = "midnightblue")
            for i in range (1, 4):
                if tic_x - spacing * i > margin - 5:
                    ticline2 = Rect(insert = (tic_x - spacing * i, width + margin * 2 - 5 - 1), size = (0.1, 1), fill = "midnightblue")
                    self.elements.append(ticline2)
            self.elements.append(ticline)
            self.elements.append(ticmarker)

    def add_ytics(self):
        maxh, margin = max(self.Y), self.margin
        scale_y, offset_y = self.scale_y, self.offset_y
        ytics = [0, 0.2, 0.4, 0.6, 0.8, 1]
        ytics = [round(offset_y - y * scale_y, 3) for y in ytics]
        spacing = (ytics[0] - ytics[1]) / 2
        for tic in ytics:
            ticline = Rect(insert = (margin - 5 - 1, tic), size = (2, 0.1), fill = "midnightblue")
            ticline2 = Rect(insert = (margin - 5, tic - spacing), size = (1, 0.1), fill = "midnightblue")
            tic_x = margin - 13
            tic_y = tic + 1
            label = str(round((offset_y - tic) / scale_y, 1))
            if len(label) == 1:
                tic_x = tic_x + 3
            if len(label) == 2:
                tic_x = tic_x + 2
            ticmarker = (Text(label, insert = (tic_x, tic_y), fill = "midnightblue", font_size = "3"))
            self.elements.append(ticline)
            self.elements.append(ticline2)
            self.elements.append(ticmarker)

    def add_axis(self):
        margin = self.margin
        width = self.width
        x_axis = Rect(insert = (margin - 5, width + margin * 2 - 5),
                size = ((self.end - self.start) * self.scale_x + 10, 0.1),
                fill = "midnightblue")
        y_axis = Rect(insert = (margin - 5, margin - 8),
            size = (0.1, width + margin + 3),
            fill = "midnightblue")
        self.elements.append(x_axis)
        self.elements.append(y_axis)
        
    def makegaussian(self, mean, stddev, height):
        endpts = (sqrt((-2) * stddev * stddev * log(1.0/ height)))
        X = [0]
        X.extend([round(stddev*2.0*(i/9.0)-stddev,3) for i in range(0,10)]) #add 10 points  near mean
        X.extend([round(abs(stddev-endpts)*(i/4.0)+stddev,3) for i in range(0,5)])
        X.extend([round(abs(stddev-endpts)*(i/4.0)-2.0*stddev,3) for i in range(0,5)])
        
        X.sort()
        Y = [round(height * exp(-x ** 2 / (2.0 * stddev * stddev)), 3) for x in X]
        return X, Y
