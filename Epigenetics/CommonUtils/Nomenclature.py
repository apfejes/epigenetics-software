'''
Created on Aug 26, 2013

@author: afejes
'''

@staticmethod
def chromosome(database, chrom):
    '''Function to convert the name of a chrom to the correct string for a given database'''
    lo = database.lowercase()

    if "human" in lo:
        if chrom.startswith("chr"):
            return chrom
        else:
            return chr + str(chrom)
    elif "yeast" in lo:
        if chrom.startswith("chr"):
            return chrom
        else:
            return chr + chrom
    elif "arabidopsis" in lo:    # Note: this is currently incorrect, arabidopsis doesn't normally have chr prefix.
        if chrom.startswith("chr"):
            return chrom
        else:
            return chr + chrom
    else:
        raise Exception("Unrecognized organism database type. Nomenclature.py")



