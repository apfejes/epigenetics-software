'''
A simple plot for scattered x,y data.

@author: apfejes
'''
# from svgwrite.shapes import Rect
from svgwrite.shapes import Line
from svgwrite.shapes import Circle
from svgwrite.text import Text
from svgwrite.drawing import Drawing


# We get coordinates from querying ensembl normally but that takes time
# so here is the coordinates of the exons for the huntington gene:
# from query_ensembl import coordinates
# from query_ensembl import name, location

class ScatterPlot(object):
    '''A simple scatter diagram plot.'''


    def __init__(self, filename, x_max, y_max, **kwargs):
        '''
        Initialize this object - you need to pass it a mongo object for it to 
        operate on.
        '''
        self.filename = filename
        self.x_max = x_max
        self.y_max = y_max
        if 'x_min' in kwargs:
            self.x_min = kwargs['x_min']
        else:
            self.x_min = 0
        if 'y_min' in kwargs:
            self.y_min = kwargs['y_min']
        else:
            self.y_min = 0
        if 'height' in kwargs:
            self.height = kwargs['height']
        else:
            self.height = 600
        if 'height' in kwargs:
            self.height = kwargs['height']
        else:
            self.height = 1200
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
        self.max_x = 100
        self.max_y_value = 100
        self.data = None

        # start drawing object
        self.plot = Drawing(self.filename, debug = self.debug,
                            size = (self.height + self.margin_left + self.margin_right, self.height + self.margin_top + self.margin_bottom),
                            # viewBox = ("0 0 " + str(float(length) + 10) + " " + str(float(width) + 10)),
                            preserveAspectRatio = "xMinYMin meet")    # , size=('200mm', '150mm'), viewBox=('0 0 200 150'))
        self.plot.add(Line(start = (self.margin_left - 4, self.margin_top), end = (self.margin_left - 4, self.margin_top + self.height), stroke_width = 0.5, stroke = "black"))
        self.plot.add(Line(start = (self.margin_left, self.margin_top + self.height + 4), end = (self.margin_left + self.height, self.margin_top + self.height + 4), stroke_width = 0.5, stroke = "black"))

    def add_and_zip_data(self, x, y):
        '''adds the data to the scatter plot, using zip to asseble the x and y's.'''
        self.data = zip(x, y)

    def add_data(self, x):
        '''adds the data to the scatter plot - no zipping applied.'''
        self.data = x

    def add_regression(self, slope):
        '''place a regression line on the plot.'''
        self.max_min()
        x = self.max_x
        y = slope * x
        print "x %f y %f" % (x, y)

        if y > self.max_y_value:
            y = self.max_y_value
            x = y / slope
            print "x %f y %f" % (x, y)


        self.plot.add(Line(start = (self.margin_left, self.margin_top + self.height),
                           end = (self.x_to_printx(x), self.y_to_printy(y)),
                                  stroke_width = 1, stroke = "black"))

    def x_to_printx(self, x):
        '''transforms the x value to an x coordinate'''
        return self.margin_left + ((float(x) / self.max_x) * self.height)

    def y_to_printy(self, y):
        '''transforms the y value to a y coordinate'''
        return (self.margin_top + self.height) - ((float(y) / self.max_y_value) * self.height)


    def max_min(self):
        '''Find Max values for x and y dimensions'''
        self.max_x = self.data[0][0]
        self.max_y_value = self.data[0][1]
        for x, y in self.data:
            if x > self.max_x:
                self.max_x = x
            if y > self.max_y_value:
                self.max_y_value = y
        print "max x y : %f %f" % (self.max_x, self.max_y_value)


    def build(self):
        '''assembles the data in the scatterplot, adding the points as circles.'''
        self.max_min()
        for x, y in self.data:
            self.plot.add(Circle(center = (self.margin_left + ((x / self.max_x) * self.height),
                                          (self.margin_top + self.height) - ((y / self.max_y_value) * self.height)),
                                 r = 2, stroke_width = 0.1, stroke_linecap = 'round',
                                 stroke_opacity = 0.3, fill = "dodgerblue",
                                 fill_opacity = 0.2))
        self.plot.add(Text(self.max_x, insert = (self.margin_left + self.height - 50, self.margin_top + self.height + 20.0),
                fill = "midnightblue", font_size = "15"))
        self.data = None


    def save(self):
        '''save the plot and reset.'''
        self.plot.save()
        self.plot = None

    def to_string(self):
        '''convert the plot to string, and reset.'''
        z = self.plot.tostring()
        self.plot = None
        return z
