"""
Created on Aug 26, 2013

@author: afejes
"""

# chromosome names for yeast.
chr_yeast = {
    'chr1': 'chrI',
    'chr2': 'chrII',
    'chr3': 'chrIII',
    'chr4': 'chrIV',
    'chr5': 'chrV',
    'chr6': 'chrVI',
    'chr7': 'chrVII',
    'chr8': 'chrVIII',
    'chr9': 'chrIX',
    'chr10': 'chrX',
    'chr11': 'chrXI',
    'chr12': 'chrXII',
    'chr13': 'chrXIII',
    'chr14': 'chrXIV',
    'chr15': 'chrXV',
    'chr16': 'chrXVI'
}


@staticmethod
def chromosome(database, chrom):
    """Function to convert the name of a chrom to the correct string for
    a given database"""
    lo = database.lowercase()

    if "human" in lo:
        if chrom.startswith("chr"):
            return chrom
        else:
            return "chr" + str(chrom)
    elif "yeast" in lo:
        if chrom.startswith("chr"):
            return chrom
        else:
            return "chr" + chrom
    elif "arabidopsis" in lo:   # Note: this is currently incorrect,
                                # arabidopsis doesn't normally have chr prefix.
        if chrom.startswith("chr"):
            return chrom
        else:
            return "chr" + chrom
    else:
        raise Exception("Unrecognized organism database type. Nomenclature.py")

# Works fine.


