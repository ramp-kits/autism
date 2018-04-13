from __future__ import print_function

import argparse
import glob
import os
import shutil
import hashlib
import zipfile

try:
    from urllib.request import urlretrieve
except ImportError:
    from urllib import urlretrieve

import joblib
import numpy as np
import pandas as pd

ATLAS = ('basc064', 'basc122', 'basc197', 'craddock_scorr_mean',
         'harvard_oxford_cort_prob_2mm', 'msdl', 'power_2011')

ARCHIVE = {atlas: 'https://storage.ramp.studio/autism/{}.zip'.format(atlas)
           for atlas in ATLAS}

CHECKSUM = {
    'basc064':
    '63dfe270cbe8e5fd9d70ff88e4bd7d053b68a98eea96bacf316f7f35bce2133f',
    'basc122':
    'fae1de1c3bd72493d32da7378d0f4f5595f7e7ebe07a5f2402ec3afc0cfa2d47',
    'basc197':
    'f1692b9e2ed6017b26d2731c785f6b3e66348eb4ecae9eb3cbdb7a69419ea77d',
    'craddock_scorr_mean':
    '8952d5350812cb0e77e99187ef9eac6b67681057783e6154a4eee13eda5c8068',
    'harvard_oxford_cort_prob_2mm':
    '93a88bf18ba13f9851b5a20a42a40c84d03b4ab42ca3b48a28581b07d90dd351',
    'msdl':
    '4861c118d72ad5824594d2b9e601029dc3edde6f10e72bd9475742068475f4b3',
    'power_2011':
    '1a94384d3f0b6ea313dfc1f72005175f8546e5d82971e765b114c31c487a645c'}


def _sha256(path):
    """Calculate the sha256 hash of the file at path."""
    sha256hash = hashlib.sha256()
    chunk_size = 8192
    with open(path, "rb") as f:
        while True:
            buffer = f.read(chunk_size)
            if not buffer:
                break
            sha256hash.update(buffer)
    return sha256hash.hexdigest()


def _check_and_unzip(output_file, atlas, atlas_directory):
    checksum_download = _sha256(output_file)
    if checksum_download != CHECKSUM[atlas]:
        os.remove(output_file)
        raise IOError('The file downloaded was corrupted. Try again '
                      'to execute this script.')

    print('Decompressing the archive ...')
    zip_ref = zipfile.ZipFile(output_file, 'r')
    zip_ref.extractall(atlas_directory)
    zip_ref.close()


def _download_fmri_data(atlas):
    print('Downloading the data from {} ...'.format(ARCHIVE[atlas]))
    output_file = os.path.abspath(
        os.path.join('.', 'data', 'fmri', atlas + '.zip'))
    urlretrieve(ARCHIVE[atlas], filename=output_file)
    atlas_directory = os.path.abspath(os.path.join('.', 'data', 'fmri'))
    _check_and_unzip(output_file, atlas, atlas_directory)


def _check_integrity_atlas(atlas):
    # check that the folder is existing
    atlas_directory = os.path.abspath(os.path.join('.', 'data', 'fmri', atlas))
    if os.path.isdir(atlas_directory):
        # compute the hash of the current data present on the disk
        filenames_atlas_current = np.array(
            glob.glob(os.path.join(atlas_directory, '*', '*', '*')),
            dtype=object)
        filenames_atlas_current.sort()
        current_hash = joblib.hash(filenames_atlas_current)

        # compute the expected hash from the data set which we provide
        filenames_atlas_expected = pd.read_csv(
            os.path.abspath(os.path.join('.', 'data', 'fmri_filename.csv')),
            index_col=0)[atlas].values
        for idx in range(filenames_atlas_expected.size):
            filenames_atlas_expected[idx] = os.path.abspath(
                os.path.join('data', filenames_atlas_expected[idx]))
        filenames_atlas_expected.sort()
        expected_hash = joblib.hash(filenames_atlas_expected)

        if current_hash == expected_hash:
            return

        shutil.rmtree(atlas_directory)

    _download_fmri_data(atlas)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='Download the time series extracted from the '
        'functional MRI data using a specific atlas.')
    parser.add_argument('atlas',
                        default='all',
                        help='Name of the atlas. One of {}. To download '
                        'all atlases, use "all".'.format(ATLAS))
    atlas = parser.parse_args().atlas

    if atlas == 'all':
        for single_atlas in ATLAS:
            _check_integrity_atlas(single_atlas)
    elif atlas in ATLAS:
        _check_integrity_atlas(atlas)
    else:
        raise ValueError("'atlas' should be one of {}. Got {} instead."
                         .format(ATLAS, atlas))

    print('Downloading completed ...')
