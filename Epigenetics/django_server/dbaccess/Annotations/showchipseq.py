'''TODO: missing docstring'''

def svgcode(mongowrapper, sample_index, organism = None, chromosome = None, start = None,
            end = None, height = None, width = None,
            tss = False, cpg = False):
    '''TODO: missing docstring'''
    print("Connecting to database:")
    print("Querying...")
    docs = mongowrapper.query(collection = "waves", chromosome = chromosome, start = start, end = end)
    if tss or cpg:
        mongowrapper.getannotations(docs)
    if chromosome[0:3] != 'chr':
        chromosome = 'chr' + str(chromosome)
    return mongowrapper.svg(to_string = True,
                 title = organism + " ChIP-Seq peaks on " + chromosome + " (" + str(start) + "-" + str(end) + ")",
                 color = 'indigo',
                 height = height,
                 width = width,
                 get_tss = tss,
                 get_cpg = cpg,
                 sample_index = sample_index)
