# Jake Yeung
# 5 March 2013
# read_data.R
# Takes .RData and writes table in tab delimited format
###############################################################################
###############################################################################

rm(list=ls()) # Clear variables


# Declare functions
###############################################################################
###############################################################################
GetBetas <- function(x){
    envir = environment()
    print(envir)
    var_loaded <- load(x, envir)
    var <- mget(var_loaded, envir)
    print (class(var[[1]]))
    if (class(var[[1]]) == "MethyLumiM"){
    write.table(betas(var[[1]]), 
                file=paste(OutputDirectory, var_loaded, "_betas.txt", sep=""),
                sep="\t", quote=FALSE, row.names=FALSE, col.names=TRUE)
    write.table(pData(var[[1]]),
                file=paste(OutputDirectory, var_loaded, "_pData.txt", sep=""),
                sep="\t", quote=FALSE, row.names=FALSE, col.names=TRUE)
    } else{
    warning(paste(var_loaded), 'is not a MethyLumiM object')
    }
}

# The code
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


# Define directories, input contains .RData files, output is where we write to.
InputDirectory <- "/home/jyeung/Documents/Inputs/"
OutputDirectory <- "/home/jyeung/Documents/Outputs/"
setwd(InputDirectory)

# First, get list of .RData files in InputDirectory.
# Second, load each .RData file.
# Third, Check to see if it's a "matrix" or a "MethyLumiM" object
# Fourth, if matrix, just write the table as .txt.
# Fifth, if methylumi, get betas of methylumi object, then writes
# 1.
data_files <- list.files(pattern="*.RData")
lapply(data_files, GetBetas)





