'''
Converts CEL files to Bed file.
    Uses rpy2 library.
    robjects.r(' ') is used to talk to R. 
@author: apfejes
'''

import time
import rpy2.robjects as robjects
from rpy2.robjects.packages import importr


''' Nice implementation via http://stackoverflow.com/questions/2556108/
    how-to-replace-the-last-occurence-of-an-expression-in-a-string
'''
def rreplace(s, old, new, occurrence):
    li = s.rsplit(old, occurrence)
    return new.join(li)


def ConvertToBedViaR():

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



    celfile = "/home/afejes/Downloads/Phoebe_CEL/CEL/09-08-01_Z_set2_T7_IP.CEL"
    bpmapfile = "/home/afejes/Chip-chip/Sc03b_MR_v04.bpmap"
    bedfile = rreplace(celfile, 'CEL', 'BED', 2)

    print "input file: %s" % (celfile)
    print "Will be writing out to %s" % (bedfile)
    time0 = time.time()
    print "importing rMat and Biobase libraries"

    importr('rMAT')
    importr('Biobase')

    # print "creating seqHeader"
    # robjects.r('seqHeader <- ReadBPMAPAllSeqHeader(\"' + bpmapfile + '\")')
    print "creating scSet"
    robjects.r('ScSet <- BPMAPCelParser(\"' +
         bpmapfile + '\", c(\"' +
         celfile + '\"), verbose = FALSE, groupName = "Sc", seqName="chr")')
    print "creating data"
    robjects.r('data <- list(chrNo = ScSet@featureChromosome, probePos = ScSet@featurePosition, MATScore = exprs(ScSet))')    # last parameter is the raw data.
    print "writing table"
    robjects.r('write.table(data, file = \"' + bedfile + '\", append = FALSE, quote = FALSE, row.names = FALSE, sep = "\t")')
    time1 = time.time()
    print "Done in %i seconds" % (time1 - time0)

if __name__ == "__main__":
#     if len(sys.argv) < 2:
#         print('RData filename must be given.')
#         sys.exit()
    starttime = time.time()
    # rdata_file = sys.argv[1]
    ConvertToBedViaR()
    print('Completed %s seconds') % int((time.time() - starttime))
