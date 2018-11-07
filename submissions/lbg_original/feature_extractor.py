import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from nilearn.connectome import ConnectivityMeasure
import nilearn.signal

np.random.seed(42)


def _load_fmri(X_df, atlas_name, standardize=True):
    """Load time-series extracted from the fMRI using a specific atlas."""
    # fmri_msdl fmri_basc064 fmri_basc122 fmri_power_2011 fmri_basc197
    fmri_filenames = X_df[atlas_name]
    fmri_data = np.array([
        pd.read_csv(subject_filename, header=None).values
        for subject_filename in fmri_filenames
    ])
    motion_filenames = X_df['fmri_motions']
    fmri_data = [
        nilearn.signal.clean(
            fmri_data_sub,
            detrend=False,
            standardize=standardize,
            confounds=motion_filename)
        for (fmri_data_sub,
             motion_filename) in zip(fmri_data, motion_filenames)
    ]
    return np.array(fmri_data)


class FeatureExtractor(BaseEstimator, TransformerMixin):
    def __init__(self,
                 atlas_name_fc1='fmri_craddock_scorr_mean',
                 atlas_name_fc2='fmri_basc122',
                 atlas_name_nn1='fmri_power_2011',
                 atlas_name_nn2='fmri_basc197'):

        self.atlas_name_fc1 = atlas_name_fc1
        self.compute_fc1 = ConnectivityMeasure(
            kind='correlation', vectorize=True)
        self.atlas_name_fc2 = atlas_name_fc2
        self.compute_fc2 = ConnectivityMeasure(kind='tangent', vectorize=True)
        self.atlas_name_nn1 = atlas_name_nn1
        self.atlas_name_nn2 = atlas_name_nn2

    def fit(self, X_df, y):
        fmri_data_fc1 = _load_fmri(
            X_df, self.atlas_name_fc1, standardize=False)
        self.compute_fc1.fit(fmri_data_fc1, y)
        fmri_data_fc2 = _load_fmri(
            X_df, self.atlas_name_fc2, standardize=False)
        self.compute_fc2.fit(fmri_data_fc2, y)
        return self

    def transform(self, X_df):
        # anatomical information
        X_anat = X_df[[
            col for col in X_df.columns if col.startswith('anatomy')
        ]]
        X_anat = X_anat.drop(columns='anatomy_select')

        # fonctional connectivity
        fmri_data_fc1 = _load_fmri(
            X_df, self.atlas_name_fc1, standardize=False)
        X_fc1 = self.compute_fc1.transform(fmri_data_fc1)
        X_fc1 = pd.DataFrame(X_fc1, index=X_df.index)
        X_fc1.columns = ['fc1_{}'.format(i) for i in range(X_fc1.columns.size)]
        fmri_data_fc2 = _load_fmri(
            X_df, self.atlas_name_fc2, standardize=False)
        X_fc2 = self.compute_fc2.transform(fmri_data_fc2)
        X_fc2 = pd.DataFrame(X_fc2, index=X_df.index)
        X_fc2.columns = ['fc2_{}'.format(i) for i in range(X_fc2.columns.size)]

        # rsfmri for conv
        X_nn1 = _load_fmri(X_df, self.atlas_name_nn1, standardize=True)
        X_nn1 = pd.DataFrame(X_nn1, index=X_df.index, columns=['nn1'])
        X_nn2 = _load_fmri(X_df, self.atlas_name_nn2, standardize=True)
        X_nn2 = pd.DataFrame(X_nn2, index=X_df.index, columns=['nn2'])

        # concatenate matrices
        return pd.concat([X_anat, X_fc1, X_fc2, X_nn1, X_nn2], axis=1)
