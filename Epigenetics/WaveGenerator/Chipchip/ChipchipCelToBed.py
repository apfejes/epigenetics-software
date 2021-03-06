'''
Converts CEL files to Bed file.
    Uses rpy2 library.
    robjects.r(' ') is used to talk to R. 
@author: apfejes
'''
import sys
import time
import os
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr
import argparse
_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = _cur_dir
while ("WaveGenerator" in _root_dir):
    _root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
import StringUtils

def ConvertToBedViaR(cel_file, bpmapfile):
    '''function for t calling R to get Bed-like values'''

    # original script - minus redundant variables.
    # library(rMAT)
    # library(Biobase)
    #
    # expName    <- "2012-07-12_SIR2_IP";  # cell file name
    # bpmapFile  <- "Sc03b_MR_v04.bpmap";  # the mapping!
    # seqHeader  <- ReadBPMAPAllSeqHeader(bpmapFile);
    # arrayFile1 <- c("2012-07-12_SIR2_IP.CEL");
    # ScSet      <- BPMAPCelParser(bpmapFile, arrayFile1, verbose = FALSE, groupName = "Sc", seqName="chr");
    # data       <- list(chrNo = ScSet1@featureChromosome, probePos = ScSet1@featurePosition, MATScore = exprs(ScSet1));  # last parameter is the raw data.
    # write.table(data, file = paste(expName,"_exp1_AllData.txt",sep=''), append = FALSE, row.names = FALSE, sep = "\t");


    bedfile = StringUtils.rreplace(cel_file, 'CEL', 'BED', 2)
    bedfile += "like"

    print "input file: %s" % (cel_file)
    print "Will be writing out to %s" % (bedfile)
    print "importing rMat and Biobase libraries"

    importr('rMAT')
    importr('Biobase')

    # print "creating seqHeader"
    # robjects.r('seqHeader <- ReadBPMAPAllSeqHeader(\"' + bpmapfile + '\")')
    print "creating scSet"
    robjects.r('ScSet <- BPMAPCelParser(\"' +
         bpmapfile + '\", c(\"' +
         cel_file + '\"), verbose = FALSE, groupName = "Sc", seqName="chr")')
    print "creating data"
    robjects.r('data <- list(chrNo = ScSet@featureChromosome, probePos = ScSet@featurePosition, MATScore = exprs(ScSet))')    # last parameter is the raw data.
    print "writing table"
    robjects.r('write.table(data, file = \"' + bedfile + '\", append = FALSE, quote = FALSE, row.names = FALSE, sep = "\t")')

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("BEDlikefiles", help = "Name of the CEL file to process", type = str)
    parser.add_argument("bpmap_file", help = "bpmap file used", type = str)
    args = parser.parse_args()
    starttime = time.time()
    ConvertToBedViaR(args.BEDlikefiles, args.bpmap_file)
    print('Completed %s seconds') % int((time.time() - starttime))
