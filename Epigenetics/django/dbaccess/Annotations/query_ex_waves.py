import query_mongo
MongoCurious = query_mongo.MongoCurious

#Example of how to use the class
m= MongoCurious(collection = "waves")
m.query(chromosome = 4, start = 1000, end = 40000)
m.findprobes()
m.getwaves(tail = 5)
