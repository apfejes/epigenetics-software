'''
Created on 2013-04-16

@author: jyeung
'''

import matplotlib.pyplot as plt  # assumed to be at top of code


def makeXYPlot(x, y, xLabel, yLabel, title, sampLabel=None, color='blue'):
    """ Make a plot from a list of x, list of y. 
    xLabel, yLabel = the labels for the x and y axis respectively
    title = the top title for the plot
    sampLabel=sample labels
    Returns the plt.Figure object created.
    --show() MUST be called after this function to display the plots!--
    """
    plt.plot(x, y, label=str(sampLabel), color=color)
    plt.xlabel(xLabel, fontsize=15)
    plt.ylabel(yLabel)
    plt.title(title, fontsize=20)
    plt.legend()
    
def makeScatter(x, y, xLabel, yLabel, title, color='blue'):
    '''
    Scatterplot
    '''
    xaxis = range(1, len(xLabel)+1)
    plt.scatter(x, y, s=80, facecolors='none', edgecolors=color)
    plt.xticks(xaxis, xLabel, fontsize=10)
    plt.ylabel(yLabel, fontsize=10)
    plt.title(title, fontsize=10)
    
    
    