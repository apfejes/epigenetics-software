'''
Created on 2013-05-21

@author: sperez
'''
# import matplotlib.pyplot as plt



def makesmoothpath(X, Y):
    ''' Generates a smooth gradient on the plot. '''
    d = "M" + str(X[0]) + "," + str(Y[0]) + " " + str(X[1]) + "," + str(Y[1]) + "S"
    for i in range(2, len(X)):
        d = d + (" " + str(X[i]) + "," + str(Y[i]))
    return d


def makelinepath(X, Y):
    ''' generate a straight line (?) '''
    d = "M" + str(X[0]) + "," + str(Y[0])
    for i in range(2, len(X)):
        d = d + (" " + str(X[i]) + "," + str(Y[i]))
    return d

