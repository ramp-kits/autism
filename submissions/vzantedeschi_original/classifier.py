import numpy as np

from sklearn.base import BaseEstimator
from sklearn.calibration import CalibratedClassifierCV
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.svm import LinearSVC, SVC
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split

ATLASES = [
    'msdl', 'basc064', 'harvard_oxford_cort_prob_2mm', 'basc122', 'basc197',
    'craddock_scorr_mean', 'power_2011', 'anatomy'
]


class Classifier(BaseEstimator):
    def __init__(self):
        self.clf = MajorityVote()

    def fit(self, X, y):
        self.clf.fit(X, y)
        return self

    def predict(self, X):
        return self.clf.predict(X)

    def predict_proba(self, X):
        return self.clf.predict_proba(X)


class MajorityVote(BaseEstimator):
    def __init__(self):
        pass

    def fit(self, X, y):

        self.svms = {}

        for atlas in ATLASES:
            view_atlas = X[[col for col in X.columns if atlas in col]]
            self.svms[atlas] = make_pipeline(
                MinMaxScaler(),
                CalibratedClassifierCV(LinearSVC(dual=False, C=1.0)))
            # self.svms[atlas] = LinearSVC(dual=False, C=1.0)
            self.svms[atlas].fit(view_atlas, y)

    def predict(self, X):

        predictions = []

        for atlas in ATLASES:
            view_atlas = X[[col for col in X.columns if atlas in col]]

            labels = self.svms[atlas].predict(view_atlas)
            predictions.append(labels)

        predictions = np.vstack(predictions).astype(int)
        m = len(X)
        most_frequent_labels = np.empty(m)

        for i in range(m):
            most_frequent_labels[i] = np.argmax(np.bincount(predictions[:, i]))

        return most_frequent_labels

    def predict_proba(self, X):
        predictions = []

        for atlas in ATLASES:
            view_atlas = X[[col for col in X.columns if atlas in col]]

            probas = self.svms[atlas].predict_proba(view_atlas)
            predictions.append(probas)

        return np.mean(predictions, axis=0)
