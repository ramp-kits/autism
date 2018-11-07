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
            ConnectivityMeasure(kind="tangent", vectorize=True))

    def fit(self, X_df, y):
        fmri_filenames = X_df['fmri_basc197']
        self.transformer_fmri.fit(fmri_filenames, y)
        return self

    def transform(self, X_df):
        fmri_filenames = X_df['fmri_basc197']
        X_connectome = self.transformer_fmri.transform(fmri_filenames)
        X_connectome = pd.DataFrame(X_connectome, index=X_df.index)
        X_connectome.columns = [
            'connectome_{}'.format(i) for i in range(X_connectome.columns.size)
        ]
        # get the anatomical information
        X_anatomy = X_df[[
            col for col in X_df.columns if col.startswith('anatomy')
        ]]
        X_anatomy = X_anatomy.drop(labels='anatomy_select', axis=1)
        X_participants = X_df[[
            col for col in X_df.columns if col.startswith('participants')
        ]]
        SEX_MAP = {"M": 0, "F": 1}
        site_encoded = pd.get_dummies(
            X_participants["participants_site"], prefix="site")
        X_participants = pd.concat(
            (X_participants["participants_age"],
             X_participants["participants_sex"].map(SEX_MAP), site_encoded),
            axis=1)

        # concatenate matrices
        return pd.concat([X_connectome, X_anatomy, X_participants], axis=1)
