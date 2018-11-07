import time
import numpy as np
from sklearn.base import BaseEstimator
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.svm import SVC


class Classifier(BaseEstimator):
    def __init__(self):

        self.connect_clfs = [
            LogisticRegression(penalty='l2', C=1.0),
            LogisticRegression(penalty='l2', C=100.0),
            LogisticRegression(penalty='l1'),
            RandomForestClassifier(max_depth=20, n_jobs=4),
            GradientBoostingClassifier(learning_rate=0.1, n_estimators=50),
            GradientBoostingClassifier(
                loss="exponential", learning_rate=0.01, n_estimators=80),
            SVC(probability=True),
            SVC(C=1e2, probability=True)
        ]
        self.anatomy_clfs = [
            LogisticRegression(penalty='l2', C=1.0),
            LogisticRegression(penalty='l2', C=100.0),
            LogisticRegression(penalty='l1'),
            RandomForestClassifier(max_depth=20, n_jobs=4),
            GradientBoostingClassifier(learning_rate=0.1, n_estimators=50),
            GradientBoostingClassifier(
                loss="exponential", learning_rate=0.01, n_estimators=80),
            SVC(probability=True),
            SVC(C=1e2, probability=True)
        ]

        self.clfs_connectome = [
            make_pipeline(StandardScaler(), reg) for reg in self.connect_clfs
        ]
        self.clfs_anatomy = [
            make_pipeline(StandardScaler(), reg) for reg in self.anatomy_clfs
        ]

        self.meta_clf = LogisticRegression(C=1.)

    def _fit_connectome(self, X_connect, y):
        for clf in self.clfs_connectome:
            print("Fitting ", clf, end="")
            start = time.time()
            clf.fit(X_connect, y)
            print(", Done in %.3f min" % ((time.time() - start) / 60))

    def _predict_connectome(self, X_connect):
        res = []
        for clf in self.clfs_connectome:
            res.append(clf.predict_proba(X_connect))
        return np.concatenate(res, axis=1)

    def _fit_anatomy(self, X_anatomy, y):
        for clf in self.clfs_anatomy:
            print("Fitting ", clf, end="")
            start = time.time()
            clf.fit(X_anatomy, y)
            print(", Done in %.3f min" % ((time.time() - start) / 60))

    def _predict_anatomy(self, X_connect):
        res = []
        for clf in self.clfs_anatomy:
            res.append(clf.predict_proba(X_connect))
        return np.concatenate(res, axis=1)

    def fit(self, X, y):
        X_anatomy = X[[col for col in X.columns if col.startswith('anatomy')]]
        X_connectome = X[[
            col for col in X.columns if col.startswith('connectome')
        ]]

        self._fit_connectome(X_connectome, y)
        self._fit_anatomy(X_anatomy, y)
        y_connectome_pred = self._predict_connectome(X_connectome)
        y_anatomy_pred = self._predict_anatomy(X_anatomy)

        self.meta_clf.fit(
            np.concatenate([y_connectome_pred, y_anatomy_pred], axis=1), y)
        return self

    def predict(self, X):
        X_anatomy = X[[col for col in X.columns if col.startswith('anatomy')]]
        X_connectome = X[[
            col for col in X.columns if col.startswith('connectome')
        ]]

        y_anatomy_pred = self._predict_anatomy(X_anatomy)
        y_connectome_pred = self._predict_connectome(X_connectome)

        return self.meta_clf.predict(
            np.concatenate([y_connectome_pred, y_anatomy_pred], axis=1))

    def predict_proba(self, X):
        X_anatomy = X[[col for col in X.columns if col.startswith('anatomy')]]
        X_connectome = X[[
            col for col in X.columns if col.startswith('connectome')
        ]]

        y_anatomy_pred = self._predict_anatomy(X_anatomy)
        y_connectome_pred = self._predict_connectome(X_connectome)

        return self.meta_clf.predict_proba(
            np.concatenate([y_connectome_pred, y_anatomy_pred], axis=1))
