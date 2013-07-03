'''
Created on 2013-06-10

@author: sperez
'''

from svgwrite.shapes import Rect, Circle
from svgwrite.text import Text
from svgwrite.drawing import Drawing
from svgwrite.path import Path
from math import fabs


class MethylationPlot(object):
    '''
    classdocs
    '''
    def __init__(self, filename, title, X, Y, sample_ids, color, start, end, length, margin, width):
        '''
        Initialize this object - you need to pass it a mongo object for it to 
        operate on.
        '''
        self.elements = []
        self.title = title
        self.X = X
        self.Y = zip(*Y)[0]
        self.sample_ids = sample_ids
        self.color = color
        self.start = start
        self.end = end
        self.length = length    # default = 200.0
        self.margin = margin    # default = 20.0
        self.width = width    # default = 60.0

        # create drawing
        self.plot = Drawing(filename,
                        size = (str(self.length) + "mm" , str(self.width * 1.5) + "mm"),
                        viewBox = ("0 0 " + str(self.length) + " " + str(self.width + self.margin * 2)),
                        preserveAspectRatio = "xMinYMin meet")

    def build(self):
        length, end, start, width, margin = self.length, self.end, self.start, self.width, self. margin

        offset = self.X[0]
        invertby = max(self.Y)
        self.offset_y = (width + margin) * 0.8 + margin
        scale_x = length / (end - start)
        self.scale_x = scale_x
        scale_y = (width + margin) * 0.8 / max(self.Y)
        self.scale_y = scale_y

        # scale the variables
        self.X = [round(float(item - offset) * scale_x, 3) + margin for item in self.X]
        self.Y = [round((invertby - item) * scale_y, 2) + margin for item in self.Y]


# #IF PLOTTING METHYLATION AS PATH, NOT POINTS:
# #        d contains the coordinates that make up the path
#         d = "M" + str(X[0]) + "," + str(Y[0]) + " " + str(X[1]) + "," + str(Y[1])
#         for i in range(2, len(X)):
#             d = d + (" " + str(X[i]) + "," + str(Y[i]))
# 
#         self.plot.add(Path(stroke = self.color, fill = "none", stroke_width = '0.3', d = d))


        if self.sample_ids:
            #A few random colors
            #self.colors = ['indigo','orange','blueviolet','aqua','darkred','green','lightcoral','blue','limegreen','yellow','pink','lightblue','brown', 'grey']
            #29 blue,green,grey palette
            self.colors = ['blue','cornflowerblue','darkblue','deepskyblue','darkturquoise','aquamarine',
                           'dodgerblue', 'lightblue', 'lightskyblue','lightseagreen','mediumslateblue',
                           'midnightblue','navy','mediumturquoise','limegreen','mediumspringgreen','forestgreen', 
                           'seagreen','palegreen', 'olive', 'yellowgreen','teal', 'paleturquoise',
                           'darkolivegreen','darkgreen','cadetblue', 'darkslategrey','darkseagreen','grey']
        sample_count = 0
        samples_color = {}
        
        for x, y, sample_id in zip(self.X, self.Y, self.sample_ids):
            if sample_id not in samples_color :
                sample_count += 1
                samples_color[sample_id] = self.colors[sample_count - 1]
                if sample_count == len(self.colors):
                    sample_count = 0
                elif sample_count > len(self.colors): print "Ran out of colours!"
            point = Circle(center = (x, y), r = 0.3, fill = samples_color[sample_id])
            self.elements.append(point)
             

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

    def add_xtics(self):
        end, start, width, margin = self.end, self.start, self. width, self.margin
        offset = start
        scale_x = self.scale_x
        scale_tics = 1;

        while((scale_tics * 10) < end - start):
            scale_tics *= 10;
        xtics = [i for i in range(start, end + 1) if i % (scale_tics) == 0]
        while len(xtics) < 4:
            scale_tics /= 2
            xtics += [i for i in range(start, end + 1) if i % (scale_tics) == 0 and i not in xtics]
        xtics.sort()
        spacing = fabs((margin + (xtics[1] - offset) * scale_x) - (margin + (xtics[0] - offset) * scale_x)) / 4
        for tic in xtics:
            tic_x = (margin + (tic - offset) * scale_x)
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
        
    def makegaussian(self, start,
                     end, margin, length,
                     pos, tail, offset,
                     height, stddev):
        endpts = int((sqrt((-2) * stddev * stddev * log(tail / height))))
        spacing = 64
        n_points = 0
        while n_points < 25 and spacing >= 2:
            X = []
            for i in range (-stddev, stddev, spacing):
                X.append(float(i))
            for i in range (-endpts, -stddev, spacing):
                X.append(float(i))
            for i in range (stddev, endpts, spacing):
                X.append(float(i))
            n_points = len(X)
            spacing /= 2
        if (endpts) not in X: X.append(endpts)
        X.sort()
        X = [float(x) for x in X if 0 <= (x + pos - offset) < (end - start)]
        stddev = float(stddev)
        Y = [round(height * exp(-x * x / (2 * stddev * stddev)), 2) for x in X]
        return X, Y
