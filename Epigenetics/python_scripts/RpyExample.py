'''
Created on 2013-04-05

@author: jyeung
'''

import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
grdevices = importr('grDevices')

r = robjects.r

x = robjects.IntVector(range(10))
y = r.rnorm(10)

r.setwd("/home/jyeung/Documents/rpy2_graphics/")
# r.pdf("myOut.pdf")
grdevices.pdf("grdeviceOut.pdf")
r.layout(r.matrix(robjects.IntVector([1, 2, 3, 2]), nrow=2, ncol=2))
r.plot(r.runif(10), y, xlab="runif", ylab="foo/bar", col="red")
#robjects.r['dev.off']() # r.dev.off doesn't work :(
grdevices.dev_off()



