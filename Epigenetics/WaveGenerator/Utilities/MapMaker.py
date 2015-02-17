'''
Created on 2013-03-05

@author: afejes
'''

import sys
import ReadModels

class MapMaker():
    '''A class that converts an array of coverage into a map object'''

    def __init__(self, PARAM):
        map_type = PARAM.get("map_type")
        frag_length = PARAM.get("fragment_length")
        if map_type == "Triangle":
            self.coverage_template = ReadModels.Distribution.Triangle(
                                    PARAM.get("triangle_min"),
                                    PARAM.get("triangle_median"),
                                    frag_length)
        elif map_type == "Flat":
            self.coverage_template = ReadModels.Distribution.Flat(frag_length)
        else:
            sys.exit("Unrecognized Readmodel type:", map_type)

        if PARAM.get("round_leading_edge"):
            self.coverage_template = ReadModels.Distribution.round_leading_edge(self.coverage_template)
        self.template_length = len(self.coverage_template)
        # print "template_length", self.template_length
        # map = array('I')

    def makeIslands(self, start, end, list_reads,):
        '''create islands'''

        coverage_map = [0.0] * (end - start)
        # print "coverage_map length:", end, ":", start, "=", end - start
        p = list_reads.head

        while p is not None:
            # print p.holding.left_end, "-", p.holding.right_end
            if p.holding.read2 is None:    # set tag
                read = p.holding.read1
                if read.is_reverse:

                    read_end = p.holding.right_end
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
                    read_start = p.holding.left_end
                    read_end = read_start + self.template_length
                    read_st = read_start - start

                    # print "for i in range(", read_st, ",", read_end - start
                    for i in range(read_st, read_end - start):
                        # print i
                        coverage_map[i] += self.coverage_template[i - read_st]

            else:    # PET TAG
                # print "PET"
                # sys.exit("PET not handled yet")
                read1 = p.holding.read1
                read2 = p.holding.read2

                ends = [read1.left_end,
                        read1.right_end,
                        read2.left_end,
                        read2.right_end]
                le = min(ends) - start
                re = max(ends) - start
                for i in range(le, re):    # No rounding done.
                    coverage_map[i] += self.coverage_template[i - le]
            p = p.next

        return coverage_map
