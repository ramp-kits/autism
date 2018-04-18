import os
import numpy as np
import pandas as pd

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer

from nilearn.connectome import ConnectivityMeasure


class FeatureExtractor():
    def fit(self, X_df, y):
        pass

    @staticmethod
    def _load_fmri(fmri_filenames):
        data_path = './data'
        return np.array([pd.read_csv(os.path.join(data_path, subject_filename),
                                     header=None).values
                         for subject_filename in fmri_filenames])

    def transform(self, X_df):
        # get only the time series for the MSDL atlas
        fmri_filenames = X_df['fmri_msdl']
        # make a transformer which will load the time series and compute the
        # connectome matrix
        transformer_fmri = make_pipeline(
            FunctionTransformer(func=self._load_fmri, validate=False),
            ConnectivityMeasure(kind='tangent', vectorize=True))
        X_connectome = transformer_fmri.fit_transform(fmri_filenames)
        X_connectome = pd.DataFrame(X_connectome, index=X_df.index)
        X_connectome.columns = ['connectome_{}'.format(i)
                                for i in range(X_connectome.columns.size)]
        # get the anatomical information
        X_anatomy = X_df[[col for col in X_df.columns
                          if col.startswith('anatomy')]]
        X_anatomy = X_anatomy.drop(columns='anatomy_select')
        # concatenate both matrices
        return pd.concat([X_connectome, X_anatomy], axis=1)
