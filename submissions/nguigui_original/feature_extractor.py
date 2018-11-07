import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer

from nilearn.connectome import ConnectivityMeasure


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
        self.transformer_fmri = make_pipeline(
            FunctionTransformer(func=_load_fmri, validate=False),
            ConnectivityMeasure(kind='tangent', vectorize=True))

    def fit(self, X_df, y):
        fmri_filenames = X_df['fmri_basc197']
        self.transformer_fmri.fit(fmri_filenames, y)
        return self

    def transform(self, X_df):
        fmri_filenames = X_df['fmri_basc197']
        X_sex = pd.Series([0] * X_df.shape[0], index=X_df.index)
        X_sex.loc[X_df['participants_sex'] == 'M'] = 1
        X_connectome = self.transformer_fmri.transform(fmri_filenames)
        X_connectome = pd.DataFrame(X_connectome, index=X_df.index)
        X_connectome.columns = [
            'connectome_{}'.format(i) for i in range(X_connectome.columns.size)
        ]
        X_connectome['participant_sex'] = X_sex

        #get the anatomical information
        X_anatomy = X_df[[
            col for col in X_df.columns if col.startswith('anatomy')
        ]]
        X_anatomy = X_anatomy.drop('anatomy_select', axis=1)
        X_anatomy['participant_sex'] = X_sex

        # concatenate both matrices
        return pd.concat([X_connectome, X_anatomy], axis=1)
