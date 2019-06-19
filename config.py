# -*- coding: UTF-8 -*-

"""
Configuration file
"""
import os

CHROMOSOMES = ['chr{}'.format(v) for v in range(1, 23)] + ['chrX', 'chrY']
CHROMOSOMES = ['chr22']

BASEDIR = os.path.join(os.path.split(os.path.abspath(__file__))[0])
DATADIR = os.path.join(BASEDIR, 'data')

FILENAME = 'filename'
DIRECTORY = 'dir'
URL = 'url'
URL_BASE = 'url_base'
VCF = 'vcf'

"""
Genome types
"""
GENOME_HUMAN_1K = 'human1k'


"""
Genome configurations
"""
GENOME_CONFIG_DICT = {}
GENOME_CONFIG_DICT[GENOME_HUMAN_1K] = {}
GENOME_CONFIG_DICT[GENOME_HUMAN_1K][VCF] = {}

# Human 1000 Genome Type
GENOME_CONFIG_DICT[GENOME_HUMAN_1K][FILENAME] =  '%s.fa.gz'
GENOME_CONFIG_DICT[GENOME_HUMAN_1K][DIRECTORY] = os.path.join(DATADIR, 'hg19_reference')
GENOME_CONFIG_DICT[GENOME_HUMAN_1K][URL] = "http://hgdownload.cse.ucsc.edu/goldenpath/hg19/chromosomes/"
GENOME_CONFIG_DICT[GENOME_HUMAN_1K][VCF][FILENAME] = "ALL.%s.phase3_shapeit2_mvncall_integrated_v5a.20130502.genotypes.vcf.gz"
GENOME_CONFIG_DICT[GENOME_HUMAN_1K][VCF][URL_BASE] = "ftp://ftp.1000genomes.ebi.ac.uk/vol1/ftp/release/20130502/"


"""
Libraries
"""
LIB_BASE_DIR = "libs"
LIB_FAST_TREE_DIR = "fast_tree"
