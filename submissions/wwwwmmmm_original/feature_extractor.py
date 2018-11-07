import numpy as np
import pandas as pd

from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn import preprocessing
from nilearn.connectome import ConnectivityMeasure

ATLAS = ('basc064', 'harvard_oxford_cort_prob_2mm', 'msdl', 'basc122')


def _load_fmri(fmri_filenames):
    return np.array([
        pd.read_csv(subject_filename, header=None).values
        for subject_filename in fmri_filenames
    ])


class FeatureExtractor(BaseEstimator, TransformerMixin):
    def __init__(self):
        self.transformer_fmri_dict = {
            key: make_pipeline(
                FunctionTransformer(func=_load_fmri, validate=False),
                ConnectivityMeasure(kind='tangent', vectorize=True))
            for key in ATLAS
        }

    def fit(self, X_df, y):
        for atlas_name in self.transformer_fmri_dict.keys():
            atlas_col_name = 'fmri_' + atlas_name
            fmri_filename = X_df[atlas_col_name]
            self.transformer_fmri_dict[atlas_name].fit(fmri_filename, y)

        return self

    def transform(self, X_df):
        X_anatomy = X_df[[
            col for col in X_df.columns if col.startswith('anatomy')
        ]]
        X_anatomy = X_anatomy.drop(columns='anatomy_select')

        X_anatomy_column = X_anatomy.columns
        X_anatomy_index = X_df.index

        min_max_scaler = preprocessing.MinMaxScaler()
        X_anatomy_data = min_max_scaler.fit_transform(X_anatomy)
        X_anatomy = pd.DataFrame(
            data=X_anatomy_data,
            index=X_anatomy_index,
            columns=X_anatomy_column)

        X_atlas_df = pd.DataFrame(index=X_df.index)
        for atlas_name in self.transformer_fmri_dict.keys():
            atlas_col_name = 'fmri_' + atlas_name
            fmri_filename = X_df[atlas_col_name]

            X_connectome = self.transformer_fmri_dict[atlas_name].transform(
                fmri_filename)
            X_connectome = pd.DataFrame(X_connectome, index=X_df.index)
            X_connectome.columns = [
                atlas_name + '_connectome_{}'.format(i)
                for i in range(X_connectome.columns.size)
            ]

            X_anatomy.columns = [
                atlas_name + '_' + col for col in X_anatomy_column
            ]

            X_atlas_df = pd.concat([X_atlas_df, X_anatomy, X_connectome],
                                   axis=1)

        return X_atlas_df
