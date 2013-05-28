import query_mongo
MongoCurious = query_mongo.MongoCurious

#Example of how to use the class
m= MongoCurious()
chromosomes = [21,"X"]
chromosomes = ["chr"+str(c) for c in chromosomes]
types = ["control","unstimulated", "boom", "listeria", "DS", "Control"]
projects = ["kollman", "down"]  #Add "All", None, 
i=1

for chromosome in chromosomes:
    for sampletype in types:
        for project in projects:
            print "--------Test #%i--------------------------------------" %i
            print "Query:", chromosome, project, sampletype
            m.query(chromosome = chromosome, project = project, sampletype = sampletype)
            m.findprobes()
            m.collectbetas()
            svg = m.svg(filename = "test.svg", color = "green")
            print "Passed test %i" %i
            i+=1
            