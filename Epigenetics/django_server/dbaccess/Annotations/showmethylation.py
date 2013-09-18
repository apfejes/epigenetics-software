'''Library to generate svg views of methylation data'''


def svgcode(mongowrapper, sample_index, types_index, organism = None, project = None, chromosome = None, start = None,
            end = None, height = None, width = None,
            tss = False, cpg = False, datapoints = False, peaks = False):
    '''TODO:missing docstring'''

    print("Querying...")
    docs = mongowrapper.query(collection = "methylation", project = project, chromosome = chromosome, start = start, end = end)
    if tss or cpg:
        mongowrapper.getannotations(docs)
    if chromosome[0:3] != 'chr':
        chromosome = 'chr' + str(chromosome)
    return mongowrapper.svg(to_string = True,
                 title = organism + " DNA methylation on " + chromosome + " (" + str(start) + "-" + str(end) + ")",
                 color = 'indigo',
                 height = height,
                 width = width,
                 get_tss = tss,
                 get_cpg = cpg,
                 show_points = datapoints,
                 show_peaks = peaks,
                 types_index = types_index,
                 sample_index = sample_index)

