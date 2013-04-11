'''
Created on 2013-04-05

@author: jyeung
'''

from rpy2.robjects.packages import importr
base = importr('base')
stats = importr('stats')
graphics = importr('graphics')
grdevices = importr('grDevices')

m = base.matrix(stats.rnorm(100), ncol = 5)
pca = stats.princomp(m)
grdevices.pdf("/home/jyeung/Documents/rpy2_graphics/PCA.pdf")
graphics.plot(pca, main="Eigen values")
stats.biplot(pca, main="biplot")
grdevices.dev_off()



