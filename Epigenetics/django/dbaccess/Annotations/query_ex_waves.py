import query_mongo
MongoCurious = query_mongo.MongoCurious

#Example of how to use the class
m= MongoCurious(collection = "waves")
m.query(chromosome = "chr5", start = 10000, end = 50001)
m.findprobes()
m.getwaves(tail = 1.0)
m.svg()

