'''
Created on 2013-07-11

@author: sperez
'''

class ColorPalette(object):
    '''
    Stores organization of color scheme for each part of plot.
    '''
    def __init__(self):

        self.type_count = 0

        self.counter = {}    # keeps track of

        self.types_color = {}
        self.samples_color = {}

        self.colors = {}

    def Colors(self):
        self.colors['blue'] = ['blue', 'cornflowerblue', 'darkblue', 'deepskyblue', 'darkturquoise',
                       'midnightblue', 'navy', 'dodgerblue', 'lightblue', 'lightskyblue', 'cadetblue', 'teal',
                       'paleturquoise', 'aquamarine', 'azure', 'aqua', 'lightsteelblue', 'powderblue']
        self.colors['green'] = ['lightseagreen', 'limegreen', 'lawngreen', 'olivedrab', 'chartreuse', 'mediumturquoise',
                               'mediumspringgreen', 'forestgreen', 'seagreen', 'palegreen', 'olive', 'darkcyan',
                               'yellowgreen', 'darkolivegreen', 'darkgreen', 'darkseagreen', 'lime']
        self.colors['red'] = ['orangered', 'tomato', 'orange', 'gold', 'firebrick', 'sandybrown',
                             'lightcoral', 'crimson', 'coral', 'darkred', 'indianred', 'maroon']
        self.colors['purple'] = ['darkslategrey', 'orchid', 'magenta', 'purple', 'blueviolet', 'darkviolet',
                           'pink', 'mediumslateblue', 'lightpink', 'deeppink', 'indigo', 'lavenderblush',
                           'violet', 'mediumorchid', 'mediumpurple', 'thistle', 'darkmagenta', 'plum']
        self.color_wheel = {1:'blue', 2:'red', 4:'purple', 3:'green'}

        return self.colors, self.color_wheel

    def sorter(self, sample_type, sample_id):
        # print '\n', self.counter, sample_type, sample_id
        if sample_type not in self.types_color:
            self.type_count += 1
            if self.type_count >= len(self.color_wheel.keys()):
                self.type_count = 1
            self.types_color[sample_type] = self.color_wheel[self.type_count]    # Assign a hue to sample_type
            self.counter[sample_type] = 0
            # print 'types:', self.type_count, sample_type, self.color_wheel[self.type_count]
        if sample_id not in self.samples_color:
            self.samples_color[sample_id] = self.colors[self.types_color[sample_type]][self.counter[sample_type]]
            self.counter[sample_type] += 1
            if self.counter[sample_type] >= len(self.colors[self.types_color[sample_type]]):
                self.counter[sample_type] = 0
        # print len(self.colors[self.types_color[sample_type]]), self.colors[self.types_color[sample_type]]
        if self.counter[sample_type] > len(self.colors[self.types_color[sample_type]]):
            print self.counter
            print sample_type, sample_id
            print self.types_color[sample_type]
            print self.counter[sample_type]
            print len(self.colors[self.types_color[sample_type]])
            raise ValueError("Ran out of colours!")
        sample_color = self.samples_color[sample_id]
        type_color = self.types_color[sample_type]
        # print type_color, sample_color
        return type_color, sample_color

    def colors_dict(self):
        return self.samples_color
