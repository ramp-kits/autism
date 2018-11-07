import numpy as np
from sklearn.base import BaseEstimator
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline


class Classifier(BaseEstimator):
    def __init__(self):
        self.clf = dict()

        self.fmris = [
            'msdl', 'basc064', 'basc122', 'basc197',
            'harvard_oxford_cort_prob_2mm', 'craddock_scorr_mean',
            'power_2011', "motions"
        ]

        for fmri in self.fmris:
            self.clf[fmri] = make_pipeline(StandardScaler(),
                                           LogisticRegression(C=1.))

    def fit(self, X, y):

        for fmri in self.fmris:

            columns = [c for c in X if fmri in c]
            X_ = X[columns].values
            self.clf[fmri].fit(X_, y)

        return self

    def predict(self, X):

        y_pred = dict()

        for fmri in self.fmris:

            columns = [c for c in X if fmri in c]
            X_ = X[columns].values

            y_pred[fmri] = np.expand_dims(
                self.clf[fmri].predict_proba(X_), axis=0)

        y_pred = np.mean(
            np.concatenate([y_pred[k] for k in y_pred]), axis=0)[:, 1]

        return y_pred

    def predict_proba(self, X):

        y_pred = dict()

        for fmri in self.fmris:

            columns = [c for c in X if fmri in c]
            X_ = X[columns].values

            y_pred[fmri] = np.expand_dims(
                self.clf[fmri].predict_proba(X_), axis=0)

        y_pred = np.mean(np.concatenate([y_pred[k] for k in y_pred]), axis=0)

        return y_pred
