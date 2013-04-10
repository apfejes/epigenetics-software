'''
Created on 2013-04-05

@author: jyeung
'''

from rpy2.robjects import NA_Real
from rpy2.rlike.container import TaggedList
from rpy2.robjects.packages import importr

base = importr('base')
stats = importr('stats')
grdevices = importr('grDevices')
graphics = importr('graphics')


'''
# create a numerical matrix of size 100x10 filled with NAs
m = base.matrix(NA_Real, nrow=100, ncol=10)

print m
# fill matrix
for row_i in xrange(1, 100+1):
    for col_i in xrange(1, 10+1):
        m.rx[TaggedList((row_i, ), (col_i, ))] = row_i + col_i * 100
print m
'''
# create a numerical matrix of size 100x10 filled with NAs
m = base.matrix(NA_Real, nrow=100, ncol=10)
# fill the matrix
for row_i in xrange(1, 100+1):
    for col_i in xrange(1, 10+1):
        # m.rx[TaggedList((row_i, ), (col_i, ))] = row_i + col_i * 100
        m.rx[row_i, col_i] = row_i + col_i * 100
        '''
        y = (row_i, ), (col_i, )
        x = TaggedList((row_i, ), (col_i, ))
        print x
        print y
        '''
pca = stats.princomp(m)
grdevices.pdf("/home/jyeung/Documents/rpy2_graphics/PCArandm.pdf")
graphics.plot(pca, main="Eigen values")
stats.biplot(pca, main="biplot")
grdevices.dev_off()

