# Jake Yeung
# 5 March 2013
# read_data.R
# Takes .RData and writes table in tab delimited format
###############################################################################
###############################################################################

rm(list=ls()) # Clear variables

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
data_files <- list.files()
vars = list()
for (i in 1:length(data_files)){
# 2.
    vars_loaded <- load(data_files[i])
    vars[i] <- mget(vars_loaded, parent.frame())
# 3 and 4.
    if (class(vars[[i]]) == "matrix"){
    write.table(vars[i], file=paste(OutputDirectory, vars_loaded, "_matrix.txt", sep=""), 
                sep="\t", quote=FALSE, row.names=FALSE, col.names=TRUE)
    } else if (class(vars[[i]]) == "MethyLumiM") {
# 3 and 5
    write.table(betas(vars[[i]]), 
                file=paste(OutputDirectory, vars_loaded, "_betas.txt", sep=""), 
                sep="\t", quote=FALSE, row.names=FALSE, col.names=TRUE)
    } else {
    warning(paste(vars_loaded), 'does not have a matrix or a methylumi object')
    }
}





