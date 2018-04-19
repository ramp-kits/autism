import numpy as np
import pandas as pd

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer

from nilearn.connectome import ConnectivityMeasure


def _load_fmri(fmri_filenames):
    """Load time-series extracted from the fMRI using a specific atlas."""
    return np.array([pd.read_csv(subject_filename,
                                 header=None).values
                     for subject_filename in fmri_filenames])


class FeatureExtractor():
    def fit(self, X_df, y):
        pass

    def transform(self, X_df):
        # get only the time series for the MSDL atlas
        fmri_filenames = X_df['fmri_msdl']
        # make a transformer which will load the time series and compute the
        # connectome matrix
        transformer_fmri = make_pipeline(
            FunctionTransformer(func=_load_fmri, validate=False),
            ConnectivityMeasure(kind='tangent', vectorize=True))
        return transformer_fmri.fit_transform(fmri_filenames)
