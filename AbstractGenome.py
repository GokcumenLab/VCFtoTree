"""
Define the skeleton of genome operations
"""

import abc
from GenomeUtils import GenomeUtils, Utils
import config


class AbstractGenome():
    __metaclass__ = abc.ABCMeta

    """
    Define abstract primitive operations that concrete subclasses define
    to implement steps of an algorithm.
    """

    def run(self, chromosome, start, end):
        # download ref sequence
        url = self._getSequenceUrl(chromosome)
        dir = self._getSequenceDir()
        filename = self._getSequenceFilename(chromosome)
        GenomeUtils.download_reference_sequence(url, dir, filename, chromosome)
        # unzip
        if self._isRemoteFileCompressed():
            Utils.unzip(dir,filename)
        # index

        # convert fastarray

    @abc.abstractmethod
    def _isRemoteFileCompressed(self):
        pass

    @abc.abstractmethod
    def _getSequenceUrl(self):
        pass

    @abc.abstractmethod
    def _getSequenceFilename(self, chromosome):
        pass

    @abc.abstractmethod
    def _getSequenceDir(self):
        pass

    @abc.abstractmethod
    def _index(self):
        pass

    @abc.abstractmethod
    def _convertToFastArray(self):
        pass


class Human1K(AbstractGenome):
    """
    Human 1000 Genome Type
    """

    def _isRemoteFileCompressed(self):
        return True

    def _getSequenceUrl(self, chromosome):
        return config.GENOME_CONFIG_DICT[config.GENOME_HUMAN_1K][config.URL] + self._getSequenceFilename(chromosome)

    def _getSequenceFilename(self, chromosome):
        return config.GENOME_CONFIG_DICT[config.GENOME_HUMAN_1K][config.FILENAME] % chromosome

    def _getSequenceDir(self):
        return config.GENOME_CONFIG_DICT[config.GENOME_HUMAN_1K][config.DIRECTORY]

    def _index(self):
        pass

    def _convertToFastArray(self):
        pass
