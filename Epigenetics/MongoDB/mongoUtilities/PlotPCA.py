'''
Created on 2013-04-08

@author: jyeung
'''

import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D


def PlotPCA3D(result, xlabel='xlabel', ylabel='ylabel', zlabel='zlabel',
            title='plot title'):
    '''
    Plots the results of PCA, PCA(data). 
    '''
    x = []
    y = []
    z = []
    for item in result.Y:
        x.append(item[0])
        y.append(item[1])
        z.append(item[2])
    print len(x)
    print len(y)
    print len(z)
    
    plt.close('all') # close all latent plotting windows
    fig1 = plt.figure() # Make a plotting figure
    ax = Axes3D(fig1) # use the plotting figure to create a Axis3D object.
    pltData = [x,y,z] 
    ax.scatter(pltData[0], pltData[1], pltData[2], 'bo') # make a scatter plot of blue dots from the data
     
    # make simple, bare axis lines through space:
    xAxisLine = ((min(pltData[0]), max(pltData[0])), (0, 0), (0,0)) # 2 points make the x-axis line at the data extrema along x-axis 
    ax.plot(xAxisLine[0], xAxisLine[1], xAxisLine[2], 'r') # make a red line for the x-axis.
    yAxisLine = ((0, 0), (min(pltData[1]), max(pltData[1])), (0,0)) # 2 points make the y-axis line at the data extrema along y-axis
    ax.plot(yAxisLine[0], yAxisLine[1], yAxisLine[2], 'r') # make a red line for the y-axis.
    zAxisLine = ((0, 0), (0,0), (min(pltData[2]), max(pltData[2]))) # 2 points make the z-axis line at the data extrema along z-axis
    ax.plot(zAxisLine[0], zAxisLine[1], zAxisLine[2], 'r') # make a red line for the z-axis.
     
    # label the axes 
    ax.set_xlabel("x-axis label") 
    ax.set_ylabel("y-axis label")
    ax.set_zlabel("y-axis label")
    ax.set_title("The title of the plot")
    plt.show() # show the plot
    
def PlotPCA2D(result, xlabel='xlabel', ylabel='ylabel',
            title='plot title'):
    '''
    Plots the results of PCA, PCA(data). 
    '''
    x = {}
    y = {}
    iter_count = 0
    column_count = 0
    for item in result.Y:
        if column_count not in x:
            x[column_count] = []
        x[column_count].append(item[0])
        if column_count not in y:
            y[column_count] = []
        y[column_count].append(item[0])
        iter_count += 1
        column_count = iter_count/result.numcols
    print iter_count
    print column_count
    print x.keys()
    print y.keys()
