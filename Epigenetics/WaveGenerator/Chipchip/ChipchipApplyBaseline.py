'''
Converts CEL files to Bed file.
    Uses rpy2 library.
    robjects.r(' ') is used to talk to R. 
@author: apfejes
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

import StringUtils


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

    def type(self):
        print ("Row")

    def __init__(self, chrom, pos, v):
        self.chromosome = chrom
        self.position = pos
        self.value = v

    def setv(self, v):
        self.value = v

    def toString(self):
        return "%s\t%i\t%f\n" % (self.chromosome, self.position, self.value)


def ReadBaseline(file_name, ps):
    bed = open(file_name, 'r')    # open file
    linecount = 0
    for line in bed:
        a = line.split("\t")
        ps[0][linecount] = "%s\t%s" % (a[0], a[1])
        ps[1][linecount] = float(a[2])
        linecount += 1
    bed.close()


def ApplyBaseline(index, file_in, file_out, ps):
    bed = open(file_in, 'r')    # open file
    bout = open(file_out, 'w')

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
            if ps[0][linecount] != "%s\t%s" % (a[0], a[1]):
                print "incorrectly paired probe!%s\t%i and %s\n" % (a[0], int(a[1]), ps[0][linecount])
            bout.write("%s\t%i\t%f\n" % (a[0], int(a[1]), float(a[2]) - float(ps[1][linecount])))
            linecount += 1

    bed.close()

def ProduceStats(records, ps):
    output = open("/home/afejes/baseline.bedlike", 'w')
    for r in range(1, len(ps[0])):
        avg = 0.0
        for s in range(1, len(ps)):
            # print "%i %i" % (s, r)
            avg += ps[s][r]
        avg = avg / records
        output.write("%s\t%f\n" % (ps[0][r], avg))
    output.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('path to BEDlike files must be given as a parameter, baseline file must be given as second parameter.')
        sys.exit()
    starttime = time.time()
    files = os.listdir(sys.argv[1])
    num_probes = 2635715
    print "initializing array..."
    probeset = [[0.0 for y in xrange(num_probes + 2)] for x in xrange(0, 2)]
    print "reading baseline from %s" % (sys.argv[2])
    print "probeset[%i][%i]" % (len(probeset), len(probeset[0]))
    ReadBaseline(sys.argv[2], probeset)

    print "done."
    op = StringUtils.rreplace(sys.argv[1], 'BED', 'NORMAL', 1)
    for i, f in enumerate(files):
        filetime = time.time()
        of = StringUtils.rreplace(f, 'BEDlike', '.normalized.BEDlike', 1)
        ApplyBaseline(i + 1, "%s%s" % (sys.argv[1], f), "%s%s" % (sys.argv[1], of), probeset)    # first file is first file, use zero for chr/pos
        print "File %i - %s processed in %f seconds" % (i + 1, f, time.time() - filetime)
    ProduceStats(len(files) + 1, probeset)
    print 'Completed in %s seconds' % int((time.time() - starttime))
