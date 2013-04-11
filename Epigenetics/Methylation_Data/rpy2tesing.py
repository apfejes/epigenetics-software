'''
Created on 2013-04-09

@author: jyeung
'''


import rpy2.robjects as robjects
from rpy2.robjects.packages import importr


Rlistf = robjects.r['list']
Rlist = Rlistf(range(1, 5))

print Rlist
print type(Rlist)