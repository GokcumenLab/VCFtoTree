# -*- coding: UTF-8 -*-

"""
Controller Class
"""

from GenomeUtils import GenomeUtils
from AbstractGenome import Human1K


class VcfController:
    """
    Controller class methods
    """

    def __init__(self):
        pass

    def run(self, type, chr, start, end, popList):
        genome = Human1K()
        genome.run(chr, start, end, popList)


if __name__ == "__main__":
    vcf = VcfController()
    vcf.run('', "chr1", 1, 2, ['ACB'])
