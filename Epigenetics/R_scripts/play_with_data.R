# Jake Yeung
# 8 March 2013
# play_with_data.R
# Takes M-values and plots a variety of plots
###############################################################################
###############################################################################
rm(list=ls()) # Clear variables


# The code
###############################################################################
###############################################################################
# Load required packages
library("methylumi") 
library("lumi")
library("lattice")


# Define directories, input contains .RData files, output is where we write to.
OutputDirectory <- "/home/jyeung/Documents/Outputs/"
setwd(OutputDirectory)


# First, get list of .RData files in InputDirectory.
# Second, load each .RData file.
# Third, Check to see if it's a "matrix" or a "MethyLumiM" object
# Fourth, if matrix, just write the table as .txt.
# Fifth, if methylumi, get betas of methylumi object, then writes
# 1.
pData_files <- list.files(pattern="*_pData.txt")
betas_files <- list.files(pattern="*._betas.txt")
exprs_files <- list.files(pattern="*._expression.txt")
i = 2 # Read second of list in filelist
pData <- read.table(pData_files[2], sep="\t", header=TRUE)
exprs <- read.table(exprs_files[2], sep="\t", header=TRUE)
set.seed(1) # for 
exprs_subset <- exprs[sample(1:nrow(exprs), 500), ]
pData_long <- data.frame(pData[-1], 
                         SampleLabel=factor(rep(pData[,"SampleLabel"], 
                                                 nrow(exprs_subset))),
                         mval=unlist(exprs_subset))
bwplot(mval~SampleLabel, pData_long)

