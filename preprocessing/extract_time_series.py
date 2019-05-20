"""This script aimed at extracting several time-series for the IMPAC challenge.

Parameters
----------
PATH_TO_DATA : list of str
    The path to the subjects with possibility to use a wildcard, e.g.
    ['/example/*', '/anotherone/*].

SUBJECTS_EXCLUDED : str
    Path to a csv containing a column 'subject_id' with the id of the patient
    to be excluded.

PATH_OUTPUT : str
    Location to dump the pickle of the timeseries. Each subject will be then
    dumped in a
    `PATH_OUTPUT/subject_id/atlas_descr/subject_id_task-Rest_confounds.pkl`

PATH_TO_RESTING_STATE : str
    Path to the resting functional MRI in each subject folder. Default is
    'session_1/rest_1/rest_res2standard.nii.gz'

PATH_TO_MOTION_CORRECTION : str
    Path to the motion correction parameters which is located in each subject
    folder. Default is 'session_1/rest_1/rest_mc.1D'.

ATLASES : list of atlases
    A list of the atlases to use.

ATLASES_DESCR : list of atlases names
    A list of the ATLASES name to store properly the data later on.

N_JOBS : int
    The number of workers. The parallel computation is performed for the
    subjects.

"""

import glob
from os import makedirs, listdir
from os.path import join, basename, normpath, exists, isdir
from shutil import copy

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from joblib import Parallel, delayed

from sklearn.datasets.base import Bunch
from sklearn.externals import six

from nilearn import image
from nilearn._utils import check_niimg
from nilearn.input_data import (NiftiLabelsMasker, NiftiMapsMasker,
                                NiftiSpheresMasker)
from nilearn.datasets import (fetch_atlas_basc_multiscale_2015,
                              fetch_atlas_msdl, fetch_atlas_craddock_2012,
                              fetch_atlas_harvard_oxford,
                              fetch_coords_power_2011)
from nilearn.connectome import ConnectivityMeasure


def _make_masker_from_atlas(atlas, memory=None, memory_level=1):
    """Construct a maker from a given atlas.

    Parameters
    ----------
    atlas : str or 3D/4D Niimg-like object,
        The atlas to use to create the masker. If string, it should corresponds
        to the path of a Nifti image.

    memory : instance of joblib.Memory or string, (default=None)
        Used to cache the masking process. By default, no caching is done. If a
        string is given, it is the path to the caching directory.

    memory_level : integer, optional (default=1)
        Rough estimator of the amount of memory used by caching. Higher value
        means more memory for caching.

    Returns
    -------
    masker : Nilearn Masker
        Nilearn Masker.

    """

    if isinstance(atlas, six.string_types):
        atlas_ = check_niimg(atlas)
        atlas_dim = len(atlas_.shape)
        if atlas_dim == 3:
            masker = NiftiLabelsMasker(atlas_,
                                       memory=memory,
                                       memory_level=memory_level,
                                       smoothing_fwhm=6,
                                       detrend=True,
                                       verbose=1)
        elif atlas_dim == 4:
            if 'craddock' in atlas:
                atlas_ = image.index_img(atlas_, 25)
                masker = NiftiLabelsMasker(atlas_,
                                           memory=memory,
                                           memory_level=memory_level,
                                           smoothing_fwhm=6,
                                           detrend=True,
                                           verbose=1)
            else:
                masker = NiftiMapsMasker(atlas_,
                                         memory=memory,
                                         memory_level=memory_level,
                                         smoothing_fwhm=6,
                                         detrend=True,
                                         verbose=1)
    else:
        coords = np.vstack((atlas.rois['x'],
                            atlas.rois['y'],
                            atlas.rois['z'])).T
        # check the radius for the sphere
        masker = NiftiSpheresMasker(seeds=coords,
                                    radius=5.,
                                    memory=memory,
                                    memory_level=memory_level,
                                    smoothing_fwhm=6,
                                    detrend=True,
                                    verbose=1)

    return masker


def _extract_timeseries(func,
                        atlas=fetch_atlas_basc_multiscale_2015().scale064,
                        confounds=None,
                        memory=None,
                        memory_level=1):
    """Extract time series for a list of functional volume.

    Parameters
    ----------
    func : str,
        Path of Nifti volumes.

    atlas : str or 3D/4D Niimg-like object, (default=BASC64)
        The atlas to use to create the masker. If string, it should corresponds
        to the path of a Nifti image.

    confounds : str,
        Path containing the confounds.

    memory : instance of joblib.Memory or string, (default=None)
        Used to cache the masking process. By default, no caching is done. If a
        string is given, it is the path to the caching directory.

    memory_level : integer, optional (default=1)
        Rough estimator of the amount of memory used by caching. Higher value
        means more memory for caching.

    n_jobs : integer, optional (default=1)
        Used to process several subjects in parallel.
        If -1, then the number of jobs is set to the number of
        cores.
    """

    try:
        masker = _make_masker_from_atlas(atlas, memory=memory,
                                         memory_level=memory_level)
        if confounds is not None:
            confounds_ = np.loadtxt(confounds)
        else:
            confounds_ = None

        return masker.fit_transform(func, confounds=confounds_)

    except ValueError as e:
        print(str(e))

# pylint: disable=invalid-name

N_JOBS = 4

###############################################################################
# Path definition

PATH_TO_DATA = ['/home/lemaitre/Documents/data/INST/*']
SUBJECTS_EXCLUDED = ('/home/lemaitre/Documents/data/'
                     'inst_excluded_subjects.csv')
PATH_OUTPUT = '/home/lemaitre/Documents/data/INST_time_series'

subjects_path = []
for pdata in PATH_TO_DATA:
    subjects_path += glob.glob(pdata)
subjects_path = sorted(subjects_path)
subjects_path = [sp for sp in subjects_path if isdir(sp)]

PATH_TO_RESTING_STATE = 'session_1/rest_1/rest_res2standard.nii.gz'
PATH_TO_MOTION_CORRECTION = 'session_1/rest_1/rest_mc.1D'

# path to the atlases
ATLASES = [fetch_atlas_msdl().maps,
           fetch_atlas_basc_multiscale_2015().scale064,
           fetch_atlas_basc_multiscale_2015().scale122,
           fetch_atlas_basc_multiscale_2015().scale197,
           fetch_atlas_harvard_oxford(atlas_name='cort-prob-2mm').maps,
           fetch_atlas_craddock_2012().scorr_mean,
           fetch_coords_power_2011()]
ATLASES_DESCR = ['msdl', 'basc064', 'basc122', 'basc197',
                 'harvard_oxford_cort_prob_2mm', 'craddock_scorr_mean',
                 'power_2011']

# load the list of patient to exclude
excluded_subjects = pd.read_csv(
    SUBJECTS_EXCLUDED,
    dtype={'subject_id': object})['subject_id'].tolist()

###############################################################################
# Build the list with all path
dataset = {'func': [], 'motion': [], 'subject_id': [], 'run': []}
for i, path_subject in enumerate(subjects_path):
    subject_id = basename(normpath(path_subject))
    if subject_id in excluded_subjects:
        continue
    content_dir = listdir(path_subject)
    run_path = sorted([folder
                       for folder in content_dir
                       if isdir(join(path_subject, folder)) and
                       'run_' in folder])
    for rp in run_path:
        dataset['subject_id'].append(subject_id)
        dataset['run'].append(rp)
        dataset['func'].append(join(path_subject, rp,
                                    PATH_TO_RESTING_STATE))
        dataset['motion'].append(join(path_subject, rp,
                                      PATH_TO_MOTION_CORRECTION))
# Create a Bunch object
dataset = Bunch(**dataset)

for atlas, atlas_descr in zip(ATLASES, ATLASES_DESCR):

    # Do not include the confounds when extracting the time series
    time_series = Parallel(n_jobs=N_JOBS, verbose=1)(
        delayed(
            _extract_timeseries)(func, atlas=atlas, confounds=None)
        for func, confounds in zip(dataset.func, dataset.motion))

    for ts, subject_id, rp, original_confound in zip(time_series,
                                                     dataset.subject_id,
                                                     dataset.run,
                                                     dataset.motion):
        # skip subjects for which time series extraction did not work
        if ts is None:
            continue
        # store the time series
        path_subject = join(PATH_OUTPUT, atlas_descr, subject_id, rp)
        if not exists(path_subject):
            makedirs(path_subject)
        filename = join(path_subject,
                        '%s_task-Rest_confounds.csv' % subject_id)
        np.savetxt(filename, ts, delimiter=',')
        # store the confounds in a separate directories
        path_subject = join(PATH_OUTPUT, 'motions', subject_id, rp)
        if not exists(path_subject):
            makedirs(path_subject)
        copy(original_confound, join(path_subject, 'motions.txt'))
        # store the matrix of correlation for MSDL
        if atlas_descr == 'msdl':
            path_subject = join(PATH_OUTPUT, 'correlation')
            if not exists(path_subject):
                makedirs(path_subject)
            connectivity_measure = ConnectivityMeasure(kind='correlation')
            correlation_matrix = connectivity_measure.fit_transform([ts])[0]
            plt.figure()
            np.fill_diagonal(correlation_matrix, 0)
            plt.imshow(correlation_matrix, vmin=-1., vmax=1., cmap='RdBu_r',
                       interpolation='nearest')
            plt.colorbar()
            plt.title('Correlation matrix MSDL atlas')
            path_image = join(path_subject, subject_id + '_' + rp + '.png')
            plt.savefig(path_image, bbox_inches='tight')
