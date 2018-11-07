import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer

from nilearn.connectome import ConnectivityMeasure
from nilearn import signal


def _load_fmri(fmri_filenames):
    """Load time-series extracted from the fMRI using a specific atlas."""
    cleaned_sr = []
    for i in range(fmri_filenames[0].shape[0]):
        # read confounds and timeseries then clean
        confounds = np.loadtxt(fmri_filenames[1].values[i])
        timeseries = pd.read_csv(
            fmri_filenames[0].values[i], header=None).values

        cleaned_sr.append(
            signal.clean(
                timeseries,
                confounds=confounds,
                standardize=False,
                detrend=True))
    return np.asarray(cleaned_sr)


class FeatureExtractor(BaseEstimator, TransformerMixin):
    def __init__(self):
        # make a transformer which will load the time series and compute the
        # connectome matrix
        self.transformer_fmri_msdl = make_pipeline(
            FunctionTransformer(func=_load_fmri, validate=False),
            ConnectivityMeasure(kind='tangent', vectorize=True))
        self.transformer_fmri_power = make_pipeline(
            FunctionTransformer(func=_load_fmri, validate=False),
            ConnectivityMeasure(kind='tangent', vectorize=True))
        self.transformer_fmri_harvard = make_pipeline(
            FunctionTransformer(func=_load_fmri, validate=False),
            ConnectivityMeasure(kind='tangent', vectorize=True))
        self.transformer_fmri_craddock = make_pipeline(
            FunctionTransformer(func=_load_fmri, validate=False),
            ConnectivityMeasure(kind='tangent', vectorize=True))
        self.transformer_fmri_basc197 = make_pipeline(
            FunctionTransformer(func=_load_fmri, validate=False),
            ConnectivityMeasure(kind='tangent', vectorize=True))
        self.transformer_fmri_basc122 = make_pipeline(
            FunctionTransformer(func=_load_fmri, validate=False),
            ConnectivityMeasure(kind='tangent', vectorize=True))
        self.transformer_fmri_basc064 = make_pipeline(
            FunctionTransformer(func=_load_fmri, validate=False),
            ConnectivityMeasure(kind='tangent', vectorize=True))

    def fit(self, X_df, y):
        fmri_filenames_msdl = [X_df['fmri_msdl'], X_df['fmri_motions']]
        fmri_filenames_power = [X_df['fmri_power_2011'], X_df['fmri_motions']]
        fmri_filenames_harvard = [
            X_df['fmri_harvard_oxford_cort_prob_2mm'], X_df['fmri_motions']
        ]
        fmri_filenames_craddock = [
            X_df['fmri_craddock_scorr_mean'], X_df['fmri_motions']
        ]
        fmri_filenames_basc197 = [X_df['fmri_basc197'], X_df['fmri_motions']]
        fmri_filenames_basc122 = [X_df['fmri_basc122'], X_df['fmri_motions']]
        fmri_filenames_basc064 = [X_df['fmri_basc064'], X_df['fmri_motions']]

        self.transformer_fmri_msdl.fit(fmri_filenames_msdl, y)
        self.transformer_fmri_power.fit(fmri_filenames_power, y)
        self.transformer_fmri_harvard.fit(fmri_filenames_harvard, y)
        self.transformer_fmri_craddock.fit(fmri_filenames_craddock, y)
        self.transformer_fmri_basc197.fit(fmri_filenames_basc197, y)
        self.transformer_fmri_basc122.fit(fmri_filenames_basc122, y)
        self.transformer_fmri_basc064.fit(fmri_filenames_basc064, y)

        return self

    def transform(self, X_df):
        fmri_filenames_msdl = [X_df['fmri_msdl'], X_df['fmri_motions']]
        fmri_filenames_power = [X_df['fmri_power_2011'], X_df['fmri_motions']]
        fmri_filenames_harvard = [
            X_df['fmri_harvard_oxford_cort_prob_2mm'], X_df['fmri_motions']
        ]
        fmri_filenames_craddock = [
            X_df['fmri_craddock_scorr_mean'], X_df['fmri_motions']
        ]
        fmri_filenames_basc197 = [X_df['fmri_basc197'], X_df['fmri_motions']]
        fmri_filenames_basc122 = [X_df['fmri_basc122'], X_df['fmri_motions']]
        fmri_filenames_basc064 = [X_df['fmri_basc064'], X_df['fmri_motions']]

        X_connectome_msdl = self.transformer_fmri_msdl.transform(
            fmri_filenames_msdl)
        X_connectome_msdl = pd.DataFrame(X_connectome_msdl, index=X_df.index)
        X_connectome_msdl.columns = [
            'connectome_msdl_{}'.format(i)
            for i in range(X_connectome_msdl.columns.size)
        ]
        X_connectome_power = self.transformer_fmri_power.transform(
            fmri_filenames_power)
        X_connectome_power = pd.DataFrame(X_connectome_power, index=X_df.index)
        X_connectome_power.columns = [
            'connectome_power_{}'.format(i)
            for i in range(X_connectome_power.columns.size)
        ]
        X_connectome_harvard = self.transformer_fmri_harvard.transform(
            fmri_filenames_harvard)
        X_connectome_harvard = pd.DataFrame(
            X_connectome_harvard, index=X_df.index)
        X_connectome_harvard.columns = [
            'connectome_harvard_{}'.format(i)
            for i in range(X_connectome_harvard.columns.size)
        ]
        X_connectome_craddock = self.transformer_fmri_craddock.transform(
            fmri_filenames_craddock)
        X_connectome_craddock = pd.DataFrame(
            X_connectome_craddock, index=X_df.index)
        X_connectome_craddock.columns = [
            'connectome_craddock_{}'.format(i)
            for i in range(X_connectome_craddock.columns.size)
        ]
        X_connectome_basc197 = self.transformer_fmri_basc197.transform(
            fmri_filenames_basc197)
        X_connectome_basc197 = pd.DataFrame(
            X_connectome_basc197, index=X_df.index)
        X_connectome_basc197.columns = [
            'connectome_basc197_{}'.format(i)
            for i in range(X_connectome_basc197.columns.size)
        ]
        X_connectome_basc122 = self.transformer_fmri_basc122.transform(
            fmri_filenames_basc122)
        X_connectome_basc122 = pd.DataFrame(
            X_connectome_basc122, index=X_df.index)
        X_connectome_basc122.columns = [
            'connectome_basc122_{}'.format(i)
            for i in range(X_connectome_basc122.columns.size)
        ]
        X_connectome_basc064 = self.transformer_fmri_basc064.transform(
            fmri_filenames_basc064)
        X_connectome_basc064 = pd.DataFrame(
            X_connectome_basc064, index=X_df.index)
        X_connectome_basc064.columns = [
            'connectome_basc064_{}'.format(i)
            for i in range(X_connectome_basc064.columns.size)
        ]

        # get the anatomical information
        X_anatomy = X_df[[
            col for col in X_df.columns
            if (col.startswith('anatomy') | col.startswith('participant_sex'))
        ]]
        X_anatomy = pd.get_dummies(X_anatomy)

        return pd.concat([
            X_connectome_msdl, X_connectome_power, X_connectome_harvard,
            X_connectome_craddock, X_connectome_basc197, X_connectome_basc122,
            X_connectome_basc064, X_anatomy
        ],
                         axis=1)
