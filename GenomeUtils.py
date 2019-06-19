"""
Common Genemo Utility Functions
"""
import json
from datetime import datetime

import gzip
import os
import sys
import time
import config
import urllib
import pysam
import subprocess


class GenomeUtils(object):
    """
    A utility class that encapsulates common Genome operations
    """

    """
    Index fast array
    """
    @staticmethod
    def index_fasta(fafile):
        if (Utils.isFileExists(fafile)):
            if not os.path.isfile(fafile + '.fai'):
                try:
                    print('\n Indexing {} ...'.format(fafile))
                    pysam.faidx(self.fafile)
                    print('\n Done')
                    return True
                except:
                    print("Oops!", sys.exc_info()[0], "occured.")
            else:
                print('\n file already indexed {}'.format(fafile))
                return False

    """
    Obtain sequence from file
    """
    @staticmethod
    def obtain_seq(fafile, chrom, start, end):
        if (Utils.isFileExists(fafile)):
            exon_coord = str(chrom) + ':' + str(start) + '-' + str(end)
            sequence = pysam.faidx(fafile, exon_coord)
            return sequence

        return None


class Utils(object):
    """
    A utility class that encapsulates some common operations
    """
    @staticmethod
    def downloadRemoteFile(url, directory, fileName):
        """
        Downloads the remote file
        """
        file_path = os.path.join(directory, fileName)

        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.isfile(file_path):
            print('\n downloading file {}'.format(url))
            Utils.download(url, file_path)

        return file_path

    @staticmethod
    def reporthook(count, block_size, total_size):
        global start_time
        if count == 0:
            start_time = time.time()
            return
        duration = time.time() - start_time
        progress_size = int(count * block_size)
        speed = int(progress_size / (1024 * duration))
        percent = int(count * block_size * 100 / total_size)
        sys.stdout.write("\r...%d%%, %d MB, %d KB/s, %d seconds passed" %
                         (percent, progress_size / (1024 * 1024), speed, duration))
        sys.stdout.flush()

    @staticmethod
    def download(url, filename):
        urllib.URLopener().retrieve(url, filename, Utils.reporthook)

    @staticmethod
    def unzip(path, filename):
        dest = os.path.join(path, filename[:-3])
        # if already extracted
        if (os.path.isfile(dest)):
            print('\n already unpacked {}'.format(dest))
            return dest

        if filename[-3:] == '.gz':
            print('\n unpacking {}'.format(dest))
            with gzip.open(os.path.join(path, filename), 'rb') as gz_file:
                file_content = gz_file.read()
            with open(dest, 'wb') as datafile:
                datafile.write(file_content)

        return dest

    @staticmethod
    def isFileExists(filename):
        if os.path.isfile(filename):
            return True
        else:
            print('\n No file at {}'.format(filename))
            return False

    @staticmethod
    def runCommand(*popenargs):
        print('\n Running console command {}'.format(popenargs))
        try:
            subprocess.call(popenargs, shell=True)
        except subprocess.CalledProcessError as e:
            print e.output
