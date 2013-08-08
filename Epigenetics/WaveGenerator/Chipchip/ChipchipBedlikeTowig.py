'''
Converts CEL files to Bed file.
    Uses rpy2 library.
    robjects.r(' ') is used to talk to R. 
@author: apfejes
'''
import sys
import time
import StringUtils


class row():

    def type(self):
        print ("Row")

    def __init__(self, chrom, pos, v):
        self.chromosome = chrom
        self.position = pos
        self.value = v

    def setv(self, v):
        self.value = v

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
    f_w_name = StringUtils.rreplace(file_name, 'BEDlike', 'wig', 1)
    f = open(f_w_name, 'w')    # open file
    for x in range(len(data)):
        pass


    # for x in range(10):
        # print '(%s, %i, %f)' % (data[x].chromosome, data[x].position, data[x].value)





if __name__ == "__main__":
    if len(sys.argv) < 1:
        print('CEL filename must be given.')
        sys.exit()
    starttime = time.time()
    bedlike_file = sys.argv[1]
    FindBaseline(bedlike_file)
    print('Completed in %s seconds') % int((time.time() - starttime))
