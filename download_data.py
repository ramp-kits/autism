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

import numpy as np
import pandas as pd
# import joblib from scikit-learn to avoid an extra dependency
from sklearn.externals import joblib

ATLAS = ('basc064', 'basc122', 'basc197', 'craddock_scorr_mean',
         'harvard_oxford_cort_prob_2mm', 'msdl', 'power_2011')

ARCHIVE = {atlas: 'https://storage.ramp.studio/autism/{}.zip'.format(atlas)
           for atlas in ATLAS}

CHECKSUM = {
    'basc064':
    '75eb5ee72344d11f056551310a470d00227fac3e87b7205196f77042fcd434d0',
    'basc122':
    '2d0d2c2338f9114877a0a1eb695e73f04fc664065d1fb75cff8d59f6516b0ec7',
    'basc197':
    '68135bb8e89b5b3653e843745d8e5d0e92876a5536654eaeb9729c9a52ab00e9',
    'craddock_scorr_mean':
    '634e0bb07beaae033a0f1615aa885ba4cb67788d4a6e472fd432a1226e01b49b',
    'harvard_oxford_cort_prob_2mm':
    '638559dc4c7de25575edc02e58404c3f2600556239888cbd2e5887316def0e74',
    'msdl':
    'fd241bd66183d5fc7bdf9a115d7aeb9a5fecff5801cd15a4e5aed72612916a97',
    'power_2011':
    'd1e3cd8eaa867079fe6b24dfaee08bd3b2d9e0ebbd806a2a982db5407328990a'}


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
