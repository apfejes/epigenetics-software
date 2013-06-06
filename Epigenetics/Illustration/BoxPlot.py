# from svgwrite.shapes import Rect
from svgwrite.shapes import Line
from svgwrite.shapes import Circle
# from svgwrite.text import Text
from svgwrite.drawing import Drawing


# We get coordinates from querying ensembl normally but that takes time
# so here is the coordinates of the exons for the huntington gene:
# from query_ensembl import coordinates
# from query_ensembl import name, location

class BoxPlot(object):
    '''
    classdocs
    '''
    def __init__(self, filename, x_max, y_max, **kwargs):
        '''
        Initialize this object - you need to pass it a mongo object for it to 
        operate on.
        '''
        self.filename = filename
        self.x_max = x_max
        self.y_max = y_max
        if 'x_min' in kwargs:
            self.x_min = kwargs.x_min
        else:
            self.x_min = 0
        if 'y_min' in kwargs:
            self.y_min = kwargs.y_min
        else:
            self.y_min = 0
        if 'height' in kwargs:
            self.height = kwargs.height
        else:
            self.height = 600
        if 'width' in kwargs:
            self.width = kwargs.width
        else:
            self.width = 1200
        if 'debug' in kwargs:
            self.debug = kwargs.debug
        else:
            self.debug = True
        if 'margin_top' in kwargs:
            self.margin_top = kwargs.margin_top
        else:
            self.margin_top = 20
        if 'margin_bottom' in kwargs:
            self.margin_bottom = kwargs.margin_bottom
        else:
            self.margin_bottom = 20
        if 'margin_left' in kwargs:
            self.margin_left = kwargs.margin_left
        else:
            self.margin_left = 20
        if 'margin_right' in kwargs:
            self.margin_right = kwargs.margin_right
        else:
            self.margin_right = 20
        self.max_x = 100
        self.max_y = 100

        # start drawing object
        self.plot = Drawing(self.filename, debug = self.debug,
                            size = (self.width + self.margin_left + self.margin_right, self.height + self.margin_top + self.margin_bottom),
                            # viewBox = ("0 0 " + str(float(length) + 10) + " " + str(float(width) + 10)),
                            preserveAspectRatio = "xMinYMin meet")    # , size=('200mm', '150mm'), viewBox=('0 0 200 150'))
        self.plot.add(Line(start = (self.margin_left, self.margin_top), end = (self.margin_left, self.margin_top + self.height)))
        self.plot.add(Line(start = (self.margin_left, self.margin_top + self.height), end = (self.margin_left + self.width, self.margin_top + self.height)))

    def add_and_zip_data(self, x, y):
        self.data = zip(x, y)

    def add_data(self, x):
        self.data = x

    def scale_data(self):
        max_x = self.data[0][0]
        max_y = self.data[0][1]
        for x, y in self.data:
            if x > self.max_x:
                self.max_x = x
            if y > self.max_y:
                self.max_y = y
        print "max x y : %f %f" % (max_x, max_y)


    def build(self):
        for x, y in self.data:
            self.plot.add(Circle(center = (self.margin_left + ((x / self.max_x) * self.width),
                                          (self.margin_top + self.height) - ((y / self.max_y) * self.height)),
                                 r = 2, stroke_width = 0.1, stroke_linecap = 'round',
                                 stroke_opacity = 0.8, fill = "dodgerblue",
                                 fill_opacity = 0.5))
        self.data = None


    def save(self):
        self.plot.save()
        self.plot = None

    def to_string(self):
        return self.plot.tostring()
        self.plot = None

