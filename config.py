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

"""
Genome types
"""
GENOME_HUMAN_1K = 'human1k'


"""
Genome configurations
"""
GENOME_CONFIG_DICT = {}
GENOME_CONFIG_DICT[GENOME_HUMAN_1K] = {}

# Human 1000 Genome Type
GENOME_CONFIG_DICT[GENOME_HUMAN_1K][FILENAME] =  'chr%s.fa.gz'
GENOME_CONFIG_DICT[GENOME_HUMAN_1K][DIRECTORY] = os.path.join(DATADIR, 'hg19_reference')
GENOME_CONFIG_DICT[GENOME_HUMAN_1K][URL] = "http://hgdownload.cse.ucsc.edu/goldenpath/hg19/chromosomes/"
