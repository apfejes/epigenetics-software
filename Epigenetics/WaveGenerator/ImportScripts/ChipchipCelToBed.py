'''
Converts CEL files to Bed file.
    Uses rpy2 library.
    robjects.r(' ') is used to talk to R. 
@author: apfejes
'''

import sys
import time
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr


def ConvertToBedViaR():
    celfile = "/home/afejes/Chip-chip/2012-07-12_SIR2_IP.CEL"
    datafile = "Sc03b_MR_v04.bpmap"
    bedfile_ext = ".bed"

    importr('rMAT')
    importr('Biobase')
    robjects.r('expName   <- \"' + celfile + '\"')    # cell file name
    robjects.r('bedFile   <- paste0(expName,\"' + bedfile_ext + '\"')    # bed file name, output

    robjects.r('bpmapFile <- \"' + datafile + '\"')    # the mapping!
    robjects.r('seqHeader <- ReadBPMAPAllSeqHeader(bpmapFile)')
    robjects.r('arrayFile1 <- c(\"' + celfile + '\")')
    robjects.r('ScSet <- BPMAPCelParser(bpmapFile, arrayFile1, verbose = FALSE, groupName = "Sc", seqName="chr")')
    robjects.r('data <- list(chrNo = ScSet1@featureChromosome, probePos = ScSet1@featurePosition, MATScore = exprs(ScSet1))')    # last parameter is the raw data.


if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print('RData filename must be given.')
#         sys.exit()
    starttime = time.time()
    # rdata_file = sys.argv[1]
    ConvertToBedViaR()
    print('Completed %s seconds') % int((time.time() - starttime))
