'''TODO:missing doc string'''

def svgcode(mongowrapper, sample_index = None, organism = None, chromosome = None, project = None, start = None,
            end = None, height = None, width = None, tss = False, cpg = False,
            datapoints = False, peaks = False):
    '''TODO:missing doc string'''
    print("Querying...")
    docs = mongowrapper.query(collection = "methylation", project = project, chromosome = chromosome, start = start, end = end)
    if chromosome[0:3] != 'chr':
        chromosome = 'chr' + str(chromosome)
    methylation = mongowrapper.svg(get_elements = True,
                        color = 'indigo',
                        height = height,
                        width = width,
                        get_tss = tss,
                        get_cpg = cpg,
                        show_points = datapoints,
                        show_peaks = peaks,
                        sample_index = sample_index)

    mongowrapper.query(collection = "waves", chromosome = chromosome, start = start, end = end)
    if tss or cpg:
        mongowrapper.getannotations(docs)
    drawing = mongowrapper.svg(title = organism + " DNA methylation and ChIP-Seq peaks on " + chromosome + " (" + str(start) + "-" + str(end) + ")",
                    color = 'indigo',
                    height = height,
                    width = width,
                    get_tss = tss,
                    get_cpg = cpg,
                    sample_index = sample_index)

    drawing.add_data(methylation)

    return drawing.to_string()
