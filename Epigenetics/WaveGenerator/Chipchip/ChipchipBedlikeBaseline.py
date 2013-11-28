'''
Converts CEL files to Bed file.
    Uses rpy2 library.
    robjects.r(' ') is used to talk to R. 
@author: apfejes, sbrown
'''
import sys
import time
import os
# import gc


_cur_dir = os.path.dirname(os.path.realpath(__file__))    # where the current file is
_root_dir = os.path.dirname(_cur_dir)
while ("WaveGenerator" in _root_dir):
    _root_dir = os.path.dirname(_root_dir)
sys.path.insert(0, _root_dir)
sys.path.insert(0, _cur_dir)
sys.path.insert(0, _root_dir + os.sep + "CommonUtils")
sys.path.insert(0, _root_dir + os.sep + "WaveGenerator" + os.sep + "Utilities")



# Works fine.
chr_yeast = {
    'chr1': 'chrI',
    'chr2': 'chrII',
    'chr3': 'chrIII',
    'chr4': 'chrIV',
    'chr5': 'chrV',
    'chr6': 'chrVI',
    'chr7': 'chrVII',
    'chr8': 'chrVIII',
    'chr9': 'chrIX',
    'chr10': 'chrX',
    'chr11': 'chrXI',
    'chr12': 'chrXII',
    'chr13': 'chrXIII',
    'chr14': 'chrXIV',
    'chr15': 'chrXV',
    'chr16': 'chrXVI'
}

probeset = []

class row():
    '''Simple object that  holds a triplex of data from a bed file'''

    @staticmethod
    def type():
        '''return the name of the object - mostly for debugging purposes'''
        print ("Row")

    def __init__(self, chrom, pos, v):
        '''initialize row object'''
        self.chromosome = chrom
        self.position = pos
        self.value = v

    def setv(self, v):
        '''simple (unnecessary) setter function'''
        self.value = v

    def toString(self):
        '''format the row object as a string'''
        return "%s\t%i\t%f\n" % (self.chromosome, self.position, self.value)



def FindBaseline(index, file_name, ps):
    '''Identify the baseline value for each probe, using the average value across the whole data set.'''
    bed = open(file_name, 'r')    # open file

    first_line = True
    headers = []
    linecount = 0
    for line in bed:
        if (first_line):
            headers = line.split("\t")
            for h in range(len(headers)):
                headers[h] = headers[h].lower()
                if headers[h].find("\n") != -1:
                    headers[h] = headers[h].replace("\n", "")
            first_line = False
        else:
            a = line.split("\t")
            if index == 1:
                # print "placing in to ps[0][%s] = %s\t%s" % (linecount, a[0], a[1])
                ps[0][linecount] = "%s\t%s" % (a[0], a[1])
            ps[index][linecount] = float(a[2])
            linecount += 1
    bed.close()

def ProduceStats(records, ps):
    '''write out the baseline values for each probe'''
    # pass parameter for where to save file
    output = open(sys.argv[2], 'w')
    for r in range(0, len(ps[0])):
        avg = 0.0
        for s in range(1, len(ps)):
            # print "%i %i" % (s, r)
            avg += ps[s][r]
        avg = avg / records
        output.write("%s\t%f\n" % (ps[0][r], avg))
    output.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('path to BEDlike files, and path to save baseline file must be given as a parameter.')
        sys.exit()
    starttime = time.time()
    # files = os.listdir(sys.argv[1])
    # The following file names sent by plu to use as normal baseline, with all IP and mock removed:
    files = ['011912_GLY240_INPUT.BEDlike',
             '2011-03-30_MycEaf7_Input.BEDlike',
             '2011-12-16_IN_MycEaf7.BEDlike',
             '2012-1-10_Input_MycEaf7.BEDlike',
             '2012-2-7_BY_Eaf1-Flag_Input.BEDlike',
             '2012-2-7_W303_Eaf1-Flag_Input.BEDlike',
             '2012-2-7_W303_Eaf1-Flag_Input.BEDlike',
             '2012-2-28_Input_H2AZ-Flag_pRS314.BEDlike',
             '2012-4-4_H2AZ_Flag_pRS314_Input.BEDlike',
             '2012-03-01_input_H2A.Z.BEDlike',
             '08-09-09_Z_Input_RNA.BEDlike',
             '08-09-10_H3K79me2_Input.BEDlike',
             '08-09-11-K727G-input.BEDlike',
             '08-11-07_H3K79me2_G2_Input.BEDlike',
             '09_03_10_G1_Input.BEDlike',
             '09-07-21_MKY7_input.BEDlike',
             '11-03-17_146input_Howe.BEDlike',
             '11-03-17_WTinput_Howe.BEDlike',
             '12-08-02inputH3K79me3.BEDlike',
             '12-01-07_Cdk8flag_flag_input.BEDlike',
             'BY-input.BEDlike',
             '09-06-12_ubp8-10_H2Bub_Input.BEDlike',
             '09-05-06-K123A-H2Bub_Input.BEDlike']

    num_probes = 2635714
    print "initializing array..."
    probeset = [[0.0 for y in xrange(num_probes)] for x in xrange(0, len(files) + 1)]
    print "probeset[%i][%i]" % (len(probeset), len(probeset[0]))
    print "done."
    for i, f in enumerate(files):
        filetime = time.time()
        FindBaseline(i + 1, "%s%s" % (sys.argv[1], f), probeset)    # first file is first file, use zero for chr/pos
        print "File %i - %s processed in %f seconds" % (i + 1, f, time.time() - filetime)
    ProduceStats(len(files) + 1, probeset)
    print 'Completed in %s seconds' % int((time.time() - starttime))
