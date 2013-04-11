'''
Created on 2013-04-04

@author: jyeung
'''


import rpy2.robjects as robjects


# robjects.r.library("lattice")
# robjects.r.library("ggplot2")
# robjects.r.library("methylumi") 


pi = robjects.r['pi']
print pi

piplus2 = robjects.r('pi') + 2
print piplus2.r_repr()

pi0plus2 = robjects.r('pi')[0] + 2
print(pi0plus2)

# Running R-code from python... 
x = robjects.r('''
        f <- function(r, verbose=FALSE) {
            if (verbose) {
                cat("I am calling f().\n")
            }
            2 * pi * r
        }
        f(3)
        ''')
print x

r_f = robjects.globalenv['f']
print(r_f.r_repr())
# or
r_f = robjects.r['f']
print(r_f)

# Let's use our r function like python...
res = r_f(3)
print(r for r in res)

# Interpolating R objects into R code strings
letters = robjects.r['letters']
print letters
# rcode = 'paste(%s, collapse="-"' %(letters.r_repr())
rcode = 'paste(%s, collapse="-")' %(letters.r_repr())
print rcode
res = robjects.r(rcode)
print(res)

# Creating rpy2 vectors
res = robjects.StrVector(['abc', 'def'])
print(res.r_repr())
res = robjects.IntVector([1, 2, 3])
print(res.r_repr())
res = robjects.FloatVector([1.1, 2.2, 3.3])
print(res.r_repr())

# Creating rpy2 matrices
v = robjects.FloatVector([1.1, 2.2, 3.3, 4.4, 5.5, 6.6])
m = robjects.r['matrix'](v, nrow=2)
print(m)
print len(m)
for i in range(0, 6):
    print m[i]

# Calling R functions.
rsum = robjects.r['sum']
pysum = rsum(robjects.IntVector([1, 2, 3,]))
print pysum
print pysum[0]
print rsum(robjects.IntVector([1,2,3]))[0]

# Keywords
rsort = robjects.r['sort']
res = rsort(robjects.IntVector([1, 2, 3]), decreasing = True)
print (res.r_repr())
print([r for r in res])






    
'''
from rpy2.robjects.vectors import FloatVector
from rpy2.robjects.packages import importr
import rpy2.rinterface as ri
stats = importr('stats')

# Rosenbrock Banana function as a cost function
# (as in the R man page for optim())
def cost_f(x):
    x1 = x[0]
    x2 = x[1]
    return 100 * (x2 - x1 * x1)**2 + (1 - x1)**2

# wrap the function f so it can be exposed to R
cost_fr = ri.rternalize(cost_f)

# starting parameters
start_params = FloatVector((-1.2, 1))

# call R's optim()
res = stats.optim(start_params, cost_fr)

print cost_fr
print start_params
print res
'''