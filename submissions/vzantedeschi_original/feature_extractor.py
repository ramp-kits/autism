import time
import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer

from nilearn.connectome import ConnectivityMeasure

ATLASES_TANGENT = ['msdl', 'basc064', 'harvard_oxford_cort_prob_2mm']

ATLASES_PARCORR = ['basc122', 'basc197', 'craddock_scorr_mean', 'power_2011']


def _load_fmri(fmri_filenames):
    """Load time-series extracted from the fMRI using a specific atlas."""
    return np.array([
        pd.read_csv(subject_filename, header=None).values
        for subject_filename in fmri_filenames
    ])


class FeatureExtractor(BaseEstimator, TransformerMixin):
    def __init__(self):
        # make a transformer which will load the time series and compute the
        # connectome matrix
        self.fmri_transformers = {}

        for atlas in ATLASES_TANGENT:
            self.fmri_transformers[atlas] = make_pipeline(
                FunctionTransformer(func=_load_fmri, validate=False),
                ConnectivityMeasure(kind='tangent', vectorize=True))

        for atlas in ATLASES_PARCORR:
            self.fmri_transformers[atlas] = make_pipeline(
                FunctionTransformer(func=_load_fmri, validate=False),
                ConnectivityMeasure(
                    kind='partial correlation', vectorize=True))

    def fit(self, X_df, y):

        print("fit feature extractor")
        t0 = time.time()

        for atlas in ATLASES_TANGENT + ATLASES_PARCORR:
            key = 'fmri_' + atlas
            fmri_filenames = X_df[key]
            self.fmri_transformers[atlas].fit(fmri_filenames, y)

        t1 = time.time()
        print("time", t1 - t0, "s")

        return self

    def transform(self, X_df):

        print("transform data")
        t0 = time.time()

        # get fmri features
        X_connectome = []

        for atlas in ATLASES_TANGENT + ATLASES_PARCORR:
            key = 'fmri_' + atlas
            fmri_filenames = X_df[key]
            atlas_X = self.fmri_transformers[atlas].transform(fmri_filenames)
            atlas_X = pd.DataFrame(atlas_X, index=X_df.index)
            atlas_X.columns = [
                'connectome_{}_{}'.format(atlas, i)
                for i in range(atlas_X.columns.size)
            ]
            X_connectome.append(atlas_X)

        X_connectome = pd.concat(X_connectome, axis=1)

        # get the anatomical information
        X_anatomy = X_df[[
            col for col in X_df.columns if col.startswith('anatomy')
        ]]
        X_anatomy = X_anatomy.drop(columns='anatomy_select')

        t1 = time.time()
        print("time", t1 - t0, "s")

        # concatenate matrices
        return pd.concat([X_connectome, X_anatomy], axis=1)
