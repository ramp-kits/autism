import time
import numpy as np
import pandas as pd
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.decomposition import PCA
from nilearn.connectome import ConnectivityMeasure


def _load_fmri(fmri_filenames):
    """Load time-series extracted from the fMRI using a specific atlas."""
    data = []
    for subject_filename in fmri_filenames:
        data.append(
            pd.read_csv(subject_filename, header=None).fillna(0).values)
    return np.array(data)


def _load_motions(motions_filenames):
    data = []
    for subject_filename in motions_filenames:
        data.append(
            pd.read_csv(
                subject_filename,
                delimiter="\s+",
                header=None,
                engine="python").fillna(0).values)
    return np.array(data)


class FeatureExtractor(BaseEstimator, TransformerMixin):
    def __init__(self):
        # make a transformer which will load the time series and compute the
        # connectome matrix
        self.fmri_names = [
            "fmri_motions", "fmri_basc064", "fmri_basc122",
            "fmri_craddock_scorr_mean", "fmri_harvard_oxford_cort_prob_2mm",
            "fmri_msdl", "fmri_power_2011"
        ]
        self.fmri_transformers = {
            col: make_pipeline(
                FunctionTransformer(func=_load_fmri, validate=False),
                ConnectivityMeasure(kind='tangent', vectorize=True))
            for col in self.fmri_names if col != "fmri_motions"
        }
        self.fmri_transformers["fmri_motions"] = make_pipeline(
            FunctionTransformer(func=_load_motions, validate=False),
            ConnectivityMeasure(kind='tangent', vectorize=True))

        self.pca = PCA(n_components=0.99)

    def fit(self, X_df, y):

        fmri_filenames = {
            col: X_df[col]
            for col in X_df.columns if col in self.fmri_names
        }

        for fmri in self.fmri_names:
            if fmri in fmri_filenames.keys():
                print("Fitting", fmri, end="")
                start = time.time()
                self.fmri_transformers[fmri].fit(fmri_filenames[fmri], y)
                print(", Done in %.3f min" % ((time.time() - start) / 60))

        X_connectome = self._transform(X_df)

        self.pca.fit(X_connectome)

        return self

    def _transform(self, X_df):
        fmri_filenames = {
            col: X_df[col]
            for col in X_df.columns if col in self.fmri_names
        }
        X_connectome = []
        for fmri in fmri_filenames:
            print("Transforming", fmri, end="")
            start = time.time()
            X_connectome.append(self.fmri_transformers[fmri].transform(
                fmri_filenames[fmri]))
            print(", Done in %.3f min" % ((time.time() - start) / 60))
        return np.concatenate(X_connectome, axis=1)

    def transform(self, X_df):

        X_connectome = self.pca.transform(self._transform(X_df))
        X_connectome = pd.DataFrame(X_connectome, index=X_df.index)
        X_connectome.columns = [
            'connectome_{}'.format(i) for i in range(X_connectome.columns.size)
        ]
        # get the anatomical information
        X_part = X_df[["participants_age"]]
        X_part["participants_sex"] = X_df["participants_sex"].map(
            lambda x: 0 if x == "M" else 1)
        X_part.columns = ['anatomy_sex', 'anatomy_age']
        X_anatomy = X_df[[
            col for col in X_df.columns if col.startswith('anatomy')
        ]]
        X_anatomy = X_anatomy.drop(columns='anatomy_select')
        # concatenate both matrices
        return pd.concat([X_connectome, X_anatomy, X_part], axis=1)
