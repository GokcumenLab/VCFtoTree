# -*- coding: UTF-8 -*-

import config



class GenomeConfig(object):
    """
    Genome Configuration Class
    """
    @staticmethod
    def getBaseDir(type):
        """
        Returns base working directory of the given type
        """
        return config.GENOME_CONFIG_DICT[type][config.DIRECTORY]

    @staticmethod
    def getSequenceFileName(type, chromosome):
        """
        Returns the genome sequence filename of the given type
        """
        return config.GENOME_CONFIG_DICT[type][config.FILENAME] % chromosome

    @staticmethod
    def getSequenceUrl(type, chromosome):
        """
        Returns remote sequence URL of the given type
        """
        return config.GENOME_CONFIG_DICT[type][config.URL] + GenomeConfig.getSequenceFileName(type, chromosome)

    @staticmethod
    def getVcfFileName(type, chromosome):
        """
        Returns the VCF filename of the given type
        """
        return config.GENOME_CONFIG_DICT[type][config.VCF][config.FILENAME] % chromosome

    @staticmethod
    def getVcfUrl(type, chromosome):
        """
        Returns remote VCF URL of the given type
        """
        return config.GENOME_CONFIG_DICT[type][config.VCF][config.URL_BASE] + GenomeConfig.getVcfFileName(type, chromosome)
