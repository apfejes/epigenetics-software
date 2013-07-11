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
        self.sample_count = {}
        
        colors = {}
        colors['blue']=['blue','cornflowerblue','darkblue','deepskyblue','darkturquoise',
                       'midnightblue','navy','dodgerblue', 'lightblue', 'lightskyblue','cadetblue','teal',
                       'paleturquoise', 'aquamarine', 'azure', 'aqua', 'lightsteelblue','powderblue' ]
        colors['green']=['lightseagreen','mediumturquoise','limegreen','lawngreen', 'olivedrab', 'chartreuse',
                               'mediumspringgreen','forestgreen', 'seagreen','palegreen', 'olive', ' darkcyan',
                               'yellowgreen', 'darkolivegreen','darkgreen', 'darkseagreen', 'lime']
        colors['red']=['orangered', 'tomato','orange', 'gold', 'firebrick', 'sandybrown', 
                             'lightcoral', 'crimson', 'coral', 'darkred', 'indianred', 'maroon']
        colors['purple']=['darkslategrey','orchid', 'purple', 'blueviolet','darkviolet', 
                           'pink', 'mediumslateblue', 'lightpink', 'deeppink', 'indigo', 'lavenderblush',
                           'violet', 'mediumorchid', 'mediumpurple', 'thistle', 'darkmagenta', 'plum']
        self.colors = colors
        self.color_wheel = {1:'blue', 2:'red', 4:'purple', 3:'green'} 
    
    def Colors(self):
        print 'oh hello'
        return self.colors, self.color_wheel
    
#     def sorter(self, sample_type, sample_id):
#         
#                         if sample_type not in types_color:
#                     type_count += 1
#                     types_color[sample_type] = color_wheel[type_count] #Assign a hue to sample_type
#                     print 'types', sample_type, color_wheel[type_count]
#                 self.colors = colors[types_color[sample_type]]
#                 #print 'colors', self.colors