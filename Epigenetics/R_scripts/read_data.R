# Jake Yeung
# 5 March 2013
# read_data.R
# Takes .RData and writes table in tab delimited format
###############################################################################
###############################################################################

# Load required packages
# 
# Installing these packages on linux was a pain.
# In the end, I used sudo apt-get install r-cran-xml to install xml
# Then I installed methylumi and lumi via bioconductor
# 
# Example for installing lumi:
# source("http://bioconductor.org/biocLite.R")
# biocLite("lumi")
# 
library("methylumi") 
library("lumi")


# Load .RData files
FileDirectory <- "/home/jyeung/Documents/Project - Kollman/R file/bin"
setwd(FileDirectory)
load("20120228-01 Kollman.final.RData")


# First, write expression table from .RData and put it into tab delimited file.
# Seocnd, write experimental design into tab delimited file. 
write.exprs(Kollman.final, file="kollman_expression.txt")
write.table(pData(Kollman.final), file="kollman_pdata.txt", sep="\t",
            quote=FALSE, row.names=FALSE, col.names=TRUE)
