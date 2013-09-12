import MongoEpigeneticsWrapper

# Example of how to use the class
m = MongoEpigeneticsWrapper.MongoEpigeneticsWrapper("human_epigenetics")

chromosomes = [21]
chromosomes = ["chr" + str(c) for c in chromosomes]
types = ["unstimulated", "listeria", "DS", "Control"]
projects = ["kollman", "down"]    # Add "All", None,
i = 1

for chromosome in chromosomes:
    for sampletype in types:
        for project in projects:
            print "--------Test #%i--------------------------------------" % i
            print "Query:", chromosome, project, sampletype
            m.query(chromosome = chromosome, project = project,
                    sample_type = sampletype, start = 30390000, end = 30391000)
            m.finddocs()
            m.collectbetas()
            # svg = m.svg(filename = "test.svg", color = "green")
            print "Passed test %i" % i
            i += 1
