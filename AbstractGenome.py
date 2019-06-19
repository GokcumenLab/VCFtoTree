# -*- coding: UTF-8 -*-

"""
Define the skeleton of genome operations
"""

import abc
import os

from GenomeUtils import GenomeUtils, Utils
from GenomeConfig import GenomeConfig
import config


class AbstractGenome():
    __metaclass__ = abc.ABCMeta

    logfile = "log.txt"
    type = ""
    filename = ""
    sequence = ""
    vcfOutputFile = ""
    fastArrayOutputFile = ""

    """
    Define abstract primitive operations that concrete subclasses define
    to implement steps of an algorithm.
    """

    def run(self, chromosome, start, end, popList):
        print('\n Running for {}'.format(self.type))

        # download ref sequence
        self._downloadRefSequence(chromosome)

        # index
        self._index(chromosome, start, end)
        # reference sequence is ready
        # download and index VCF file
        self._downloadVcfFile(chromosome)
        self._indexVcf(chromosome, start, end)
        self._convertToFastArray(chromosome, start, end, popList)
        # convert fastarray

    def getBaseDir(self):
        '''
        Base working directory of type
        '''
        return GenomeConfig.getBaseDir(self.type)

    def getSequenceUrl(self, chromosome):
        return GenomeConfig.getSequenceUrl(self.type, chromosome)

    def getSequenceFilename(self, chromosome):
        return GenomeConfig.getSequenceFileName(self.type, chromosome)

    def getVcfFileName(self, chromosome):
        return GenomeConfig.getVcfFileName(self.type, chromosome)

    def getVcfUrl(self, chromosome):
        return GenomeConfig.getVcfUrl(self.type, chromosome)

    @abc.abstractmethod
    def _downloadRefSequence(self):
        pass

    @abc.abstractmethod
    def _index(self, chromosome, start, end):
        pass

    @abc.abstractmethod
    def _downloadVcfFile(self, chromosome):
        pass

    @abc.abstractmethod
    def _indexVcf(self, chromosome, start, end):
        pass

    @abc.abstractmethod
    def _convertToFastArray(self, chromosome, start, end, popList):
        pass


class Human1K(AbstractGenome):
    """
    Human 1000 Genome Type
    """

    # default constructor
    def __init__(self):
        self.type = config.GENOME_HUMAN_1K
        self.fastArrayOutputFile = os.path.join(
            self.getBaseDir(), "ALI_1000HG.fa")

    def _downloadRefSequence(self, chromosome):
        url = self.getSequenceUrl(chromosome)
        dir = self.getBaseDir()
        filename = self.getSequenceFilename(chromosome)
        Utils.downloadRemoteFile(url, dir, filename)
        # unzip
        self.filename = Utils.unzip(dir, filename)
        print('\n Ref Seq File {}'.format(self.filename))

    def _index(self, chromosome, start, end):
        GenomeUtils.index_fasta(self.filename)
        self.sequence = GenomeUtils.obtain_seq(
            self.filename, chromosome, start, end)

        print('\n sequence {}'.format(self.sequence))

    def _downloadVcfFile(self, chromosome):
        vcfFileUrl = self.getVcfUrl(chromosome)
        dir = self.getBaseDir()
        filename = self.getVcfFileName(chromosome)
        Utils.downloadRemoteFile(vcfFileUrl, dir, filename)

    def _indexVcf(self, chromosome, start, end):
        filepath = os.path.join(
            self.getBaseDir(), self.getVcfFileName(chromosome))
        region = str(chromosome) + ':' + str(start) + '-' + str(end)
        outputFilename = str(chromosome) + '_start_' + \
            str(start) + '_end' + str(end)
        self.vcfOutputFile = os.path.join(
            self.getBaseDir(), outputFilename + '.vcf')
        if not Utils.isFileExists(filepath + '.tbi'):
            tabixIndexCmd = 'tabix -h ' + filepath
            Utils.runCommand(tabixIndexCmd)
        else:
            print('\n tbi index file exists skipped indexing {}'.format(filepath))

        tabixCmd = 'tabix -h ' + filepath + ' ' + region + ' > ' + self.vcfOutputFile
        Utils.runCommand(tabixCmd)

    def _convertToFastArray(self, chromosome, start, end, popList):
        popStr = ','.join(map(str, popList))
        cmd = 'python Code/vcf2fasta_erica.py ' + self.vcfOutputFile + ' ' + self.filename + ' ' + \
            str(start) + ' ' + str(end) + ' ' + popStr + ' ' + \
            self.fastArrayOutputFile + ' ' + os.path.join(
                self.getBaseDir(), self.logfile)
        Utils.runCommand(cmd)
        # Utils.runCommand(['python','Code/vcf2fasta_erica.py',self.vcfOutputFile,  self.filename, str(start), str(end), 'ALL', self.fastArrayOutputFile,os.path.join(
        #     self.getBaseDir(), self.logfile)])
