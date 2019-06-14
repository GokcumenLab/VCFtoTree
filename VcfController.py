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

    def downloadAndIndexRefSeq(self, type, chr, start, end):
        genome = Human1K()
        genome.run(chr, start, end)


if __name__ == "__main__":
    vcf = VcfController()
    vcf.downloadAndIndexRefSeq('', 1, 10, 11)
