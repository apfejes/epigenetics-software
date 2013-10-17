'''
Created on 2013-07-11

@author: sperez
'''

class ColorPalette():
    '''
    Stores organization of color scheme for each part of plot.
    '''
    def __init__(self):
        self.type_count = 0
        self.counter = {}    # keeps track of maps
        self.types_color = {}
        self.samples_color = {}
        self.colors = {}

        # Hold dictionaries of colours for use in generating svgs
#         self.colors['blue'] = ['blue', 'cornflowerblue', 'darkblue', 'deepskyblue', 'darkturquoise',
#                        'midnightblue', 'navy', 'dodgerblue', 'lightblue', 'lightskyblue', 'cadetblue', 'teal',
#                        'paleturquoise', 'aquamarine', 'azure', 'aqua', 'lightsteelblue', 'powderblue']
#         self.colors['green'] = ['lightseagreen', 'limegreen', 'lawngreen', 'olivedrab', 'chartreuse', 'mediumturquoise',
#                                'mediumspringgreen', 'forestgreen', 'seagreen', 'palegreen', 'olive', 'darkcyan',
#                                'yellowgreen', 'darkolivegreen', 'darkgreen', 'darkseagreen', 'lime']
#         self.colors['red'] = ['orangered', 'tomato', 'orange', 'gold', 'firebrick', 'sandybrown',
#                              'lightcoral', 'crimson', 'coral', 'darkred', 'indianred', 'maroon']
#         self.colors['purple'] = ['darkslategrey', 'orchid', 'magenta', 'purple', 'blueviolet', 'darkviolet',
#                            'pink', 'mediumslateblue', 'lightpink', 'deeppink', 'indigo', 'lavenderblush',
#                            'violet', 'mediumorchid', 'mediumpurple', 'thistle', 'darkmagenta', 'plum']
        self.colors['#FF00FF'] = ['#ffccff', '#ffb9ff', '#ffa7ff', '#ff94ff', '#ff82ff', '#ff6fff', '#ff5dff', '#ff4aff', '#ff38ff', '#ff25ff', '#ff13ff', '#ff00ff']    # magenta
        self.colors['#FF0000'] = ['#ffcccc', '#ffb9b9', '#ffa7a7', '#ff9494', '#ff8282', '#ff6f6f', '#ff5d5d', '#ff4a4a', '#ff3838', '#ff2525', '#ff1313', '#ff0000']    # red
        self.colors['#00FF00'] = ['#00cc00', '#0FCF0F', '#1DD21D', '#2CD52C', '#3BD83B', '#4ADB4A', '#58DD58', '#67E067', '#76E376', '#85E685', '#93E993', '#A2ECA2']    # green
        self.colors['#0000ff'] = ['#ccccff', '#b9b9ff', '#a7a7ff', '#9494ff', '#8282ff', '#6f6fff', '#5d5dff', '#4a4aff', '#3838ff', '#2525ff', '#1313ff', '#0000ff']    # blue
        self.colors['#00ffff'] = ['#ccffff', '#b9ffff', '#a7ffff', '#94ffff', '#82ffff', '#6fffff', '#5dffff', '#4affff', '#38ffff', '#25ffff', '#13ffff', '#00ffff']    # light blue
        self.colors['#CCCC00'] = ['#cccc00', '#BFC000', '#B1B400', '#A4A700', '#969B00', '#898F00', '#7B8300', '#6E7700', '#606B00', '#535E00', '#455200', '#384600']    # yellows
        self.color_wheel = {}

        for i, j in enumerate(self.colors):
            self.color_wheel[1 + i] = j
            print "colour_wheel %i - %s" % (1 + i, j)



    def sorter(self, sample_type, sample_id):
        '''This function appears to assign colours to each sample id, based up on sample type.'''
        # print "counter=%s sample_type=%s sample_id=%s" % (self.counter, sample_type, sample_id)
        if sample_type not in self.types_color:
            self.type_count += 1
            print "self.type_count = %s " % self.type_count
            if self.type_count > len(self.color_wheel.keys()):    # this array has no zero, 1 to len(), therefore not >= len()
                self.type_count = 1
                print "resetting self.type_count = %s " % self.type_count
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
            raise ValueError("Ran out of colours! - sorter")
        sample_color = self.samples_color[sample_id]
        type_color = self.types_color[sample_type]
        # print type_color, sample_color
        return type_color, sample_color

    def assign_group_colour(self, sample_type):
        '''This function appears to assign colours to each sample id, based up on sample type.'''
        # print "counter=%s sample_type=%s" % (self.counter, sample_type)
        if sample_type not in self.types_color:
            self.type_count += 1
            if self.type_count >= len(self.color_wheel.keys()):
                self.type_count = 1
            self.types_color[sample_type] = self.color_wheel[self.type_count]    # Assign a hue to sample_type
            self.counter[sample_type] = 0
            # print 'types:', self.type_count, sample_type, self.color_wheel[self.type_count]
        # print len(self.colors[self.types_color[sample_type]]), self.colors[self.types_color[sample_type]]
        if self.counter[sample_type] > len(self.colors[self.types_color[sample_type]]):
            print self.counter
            print sample_type
            print self.types_color[sample_type]
            print self.counter[sample_type]
            print len(self.colors[self.types_color[sample_type]])
            raise ValueError("Ran out of colours! - assign_group_colour")
        type_color = self.types_color[sample_type]
        # print type_color, sample_color
        return type_color


    def get_colours(self, sample_type, sample_id):
        '''Simple method for retrieving colours we should already have in the palette.'''
        return self.types_color[sample_type], self.samples_color[sample_id]

    def get_group_colour(self, sample_type):
        '''Simple method for retrieving colours we should already have in the palette.'''
        return self.types_color[sample_type]

    def get_type_colors(self):
        '''get colours for all types'''
        return self.types_color

    def get_colors_dict(self):
        '''return the list of colour/sample mappings'''
        return self.samples_color

    def set_colors_dict(self, types, samples):
        '''return the list of colour/sample mappings'''
        self.samples_color = samples
        self.types_color = types

