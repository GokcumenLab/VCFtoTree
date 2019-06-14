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


class GenomeUtils(object):
    """
    A utility class that encapsulates common Genome operations
    """
    @staticmethod
    def download_reference_sequence(url, directory, fileName, chromosome):
        """
        Downloads the given chromosome's reference sequence
        """
        file_path = os.path.join(directory, fileName)

        if not os.path.exists(directory):
            os.makedirs(directory)

        if not os.path.isfile(file_path):
            Utils.download(url, file_path)

        return file_path


class Utils(object):
    """
    A utility class that encapsulates some common operations
    """
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
        print('\n unpacking {}'.format(filename))
        if filename[-3:] == '.gz':
            with gzip.open(os.path.join(path, filename), 'rb') as gz_file:
                file_content = gz_file.read()
            with open(os.path.join(path, filename[:-3]), 'wb') as datafile:
                datafile.write(file_content)
