'''
Created on 2013-04-02

@author: jyeung
'''


import numpy as np
import matplotlib.pyplot as plt


def PlotBarGraph(my_dict, graph_title = None):
        '''
        Takes a dictionary and plots bargraph from it. 
        '''
        labels = my_dict.keys()
        my_list = my_dict.values()
        N = len(my_list)
        ind = np.arange(N)
        width = 0.35
        p = plt.bar(ind, my_list, width, color='r')
        plt.ylabel('Average Beta Value')
        plt.title('Average Beta Value by samples in Chr 21')
        plt.xticks(ind + width / 2.0, tuple(labels))
        plt.yticks(np.arange(0, 1, 10))
        plt.show()
        
'''
test_dict = {u'C1ab F': 0.5195746266630658, u'C3a F': 0.5209056183256038, u'DS10A M': 0.5275177025356175, u'C4ab2 M': 0.5200748122812772, u'C2c M': 0.5096301426637272, u'DS05A F': 0.5067381065901574, u'DS02A F': 0.5163393060668867, u'DS01A M': 0.5289783325513938, u'C4ab1 M': 0.5188577036496421, u'DS06A M': 0.5298105925113229, u'C5a M': 0.5239496707144142, u'DS08B F': 0.5159879607074298, u'DS04A F': 0.5312867636483205, u'C2a M': 0.5102619551290094, u'DS09A M': 0.5303951209867889, u'DS03A F': 0.5062987926969229, u'DS07A M': 0.5105768727656222}
# labels = dict.keys()
PlotBarGraph(test_dict, 'bargraph test')
'''

'''     
def PlotBarGraph(list, labels):
    N = len(list)
    ind = np.arange(N)
    width = 0.35
    p = plt.bar(ind, list, width, color='r')
    plt.ylabel('Average Beta Value')
    plt.title('Average Beta Value of 100 probes across samples')
    plt.xticks(ind + width / 2.0, tuple(labels))
    plt.yticks(np.arange(0, 1, 10))
    plt.show()
'''
        
            