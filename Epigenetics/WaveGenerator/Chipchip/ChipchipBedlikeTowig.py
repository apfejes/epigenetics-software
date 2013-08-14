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
import WigFileThread


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

def FindBaseline(file_name):
    f = open(file_name, 'r')    # open file

    print "processing data file (" + file_name + ")..."
    first_line = True
    headers = []
    data = []
    for line in f:
        if (first_line):
            headers = line.split("\t")
            for h in range(len(headers)):
                headers[h] = headers[h].lower()
                if headers[h].find("\n") != -1:
                    headers[h] = headers[h].replace("\n", "")
            first_line = False
        else:
            a = line.split("\t")
            r = row(a[0], int(a[1]), float(a[2]))
            data.append(r)
    # find most common number
    f.close()
    v_sum = 0
    hist = {}
    for x in range(len(data)):
        v_sum += data[x].value
        if hist.has_key(str(data[x].value)):
            hist[str(data[x].value)] += 1
        else:
            hist[str(data[x].value)] = 1
    v_avg = v_sum / len(data)
    print "v average = %f" % (v_avg)
    point = 0
    largest = 0
    for g, y in hist.iteritems():
        if y > largest:
            largest = y
            point = g
            # print "g, y (%s, %i)" % (g, y)
    # print "point, largest (%s, %i)" % (point, largest)
    point = float(point)
    for g in range(len(data)):
        v = data[g].value - point
        if v < 0:
            v = 0
        data[g].setv(v)
    # create wig file
    f_w_name = StringUtils.rreplace(file_name, '.BEDlike', '', 1)
    f_w_name = StringUtils.rreplace(f_w_name, 'BED', 'WIG', 1)

    # print "Writing to %s" % (f_w_name)
    # f = open(f_w_name, 'w')    # open file


    current_chr = data[0].chromosome
    print "New Chromosome %s (%s)" % (current_chr, chr_yeast[current_chr])
    last_bp = 0
    last_ht = 0
    wigfile = WigFileThread.WigFileWriter(None)
    wigfile.start_wig_writer(os.path.dirname(f_w_name), os.path.basename(f_w_name))


    # for x in range (0, 5020):
    #    print "x=%i position=%i, value=%f" % (x, data[x].position + 1, data[x].value)


    x = 0
    a = 0
    # gc.disable()
    coverage_map = []
    l = len(data)
    x = 1
    block_left = 0
    while x < l:
        # print "x of len: %i/%i" % (x, l)
        if data[x].chromosome != current_chr:
            if len(coverage_map) > 0:
                wigfile.add_map(coverage_map, chr_yeast[current_chr], block_left)
                # wigfile.add_map(coverage_map, current_chr, block_left)
                coverage_map = []
            # TODO: taper off chromosome
            # TODO: taper "on" new chromosome
            print "New Chromosome %s (%s)" % (data[x].chromosome, chr_yeast[data[x].chromosome])
            current_chr = data[x].chromosome    # switch chromosomes,
        block_left = data[x - 1].position + 2    # shift by 1, and block starts after the zero.
        last_bp = data[x - 1].position + 1
        # print "x=%i data=%i, value=%f" % (x, data[x].position + 1, data[x].value)
        while x < l and data[x].value != 0:
            diff = (data[x].position + 1) - last_bp
            if diff > 6:
                diff = 6
            if (diff > 1):
                slope = float(data[x].value - last_ht) / (diff)    # slope between the two
                for y in range(1, diff):
                    coverage_map.append(round(last_ht + (slope * y), 2))
                coverage_map.append(round(data[x].value, 2))
            else:
                coverage_map.append(round(data[x].value, 2))
                a += 1
            last_bp = data[x].position + 1
            last_ht = data[x].value
            if x < l - 1 and data[x + 1].value == 0:
                diff = (data[x + 1].position + 1) - (data[x].position + 1)
                slope = float(0 - data[x].value) / (diff)
                for y in range(1, diff):
                    coverage_map.append(round(data[x].value + (slope * y), 2))
                last_ht = 0
            x += 1

        while x < l and data[x].value == 0:
            x += 1
            last_ht = 0
        if len(coverage_map) > 0:
            wigfile.add_map(coverage_map, chr_yeast[current_chr], block_left)
            # wigfile.add_map(coverage_map, current_chr, block_left)
            coverage_map = []
    # gc.enable()


    print "Closing Wigwriter.  This may take some time."
    wigfile.close_wig_writer()
    print "Wigwriter closed."

if __name__ == "__main__":
    if len(sys.argv) < 1:
        print('CEL filename must be given as a parameter.')
        sys.exit()
    starttime = time.time()
    bedlike_file = sys.argv[1]
    FindBaseline(bedlike_file)
    print 'Completed in %s seconds' % int((time.time() - starttime))
