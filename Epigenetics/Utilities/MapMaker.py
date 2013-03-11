'''
Created on 2013-03-05

@author: afejes
'''

import sys
from Utilities import ReadModels

class MapMaker():

    template_length = 0;
    coverage_template = None

    def __init__(self, map_type, parm1, parm2, parm3):
        if map_type == "Triangle":
            self.coverage_template = ReadModels.Distribution.Triangle(parm1, parm2, parm3)
        elif map_type == "Flat":
            self.coverage_template = ReadModels.Distribution.Flat(parm1)
            if parm2 != None or parm3 != None:
                sys.exit("too many parameters passed for Flat distribution")
        else:
            sys.exit("Unrecognized Readmodel type:", map_type)

        self.template_length = len(self.coverage_template)
        # print "template_length", self.template_length
        # map = array('I')



    def makeIslands(self, start, end, list_reads,):

        coverage_map = [0.0] * (end - start)
        # print "coverage_map length:", end, ":", start, "=", end - start
        p = list_reads.head

        while p != None:
            # print p.holding.get_left_end(), "-", p.holding.get_right_end()
            if p.holding.read2 == None:    # set tag
                read = p.holding.read1
                if read.is_reverse:

                    read_end = p.holding.get_right_end()
                    read_start = read_end - self.template_length
                    # print "st to end: ", read_start, "-", read_end, " t:", self.template_length

                    read_st = read_start - start
                    if read_st < 0:
                        read_st = 0    # don't start before the start of the chromosome
                    # print "for i in range(", read_st, ",", read_end - start, ")"
                    for i in range(read_st, read_end - start):
                        # print i, (template_length - i) - (read_st + 1)
                        # print i, "   (", template_length, "-1) - (", i, "-", read_st, ") + 1)"
                        coverage_map[i] += self.coverage_template[(self.template_length - 1) - (i - read_st)]
                else:    # forward
                    read_start = p.holding.get_left_end()
                    read_end = read_start + self.template_length
                    read_st = read_start - start

                    # print "for i in range(", read_st, ",", read_end - start
                    for i in range(read_st, read_end - start):
                        # print i
                        coverage_map[i] += self.coverage_template[i - read_st]

            else:    # PET TAG
                print "PET"
                sys.exit("PET not handled yet")
            p = p.next

            # if PET
            # if SET

        return coverage_map
