# define classifier
import numpy as np

from sklearn.base import BaseEstimator
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split


class Classifier(BaseEstimator):
    def __init__(self):
        self.clf_connectome = make_pipeline(StandardScaler(),
                                            LogisticRegression(C=0.1))
        self.clf_anatomy = make_pipeline(StandardScaler(),
                                         LogisticRegression(C=1))
        self.meta_clf = LogisticRegression(C=1.)

    def fit(self, X, y):
        X_anatomy = X[[col for col in X.columns if col.startswith('anatomy')]]
        X_connectome = X[[
            col for col in X.columns if col.startswith('connectome')
        ]]
        train_idx, validation_idx = train_test_split(
            range(y.size), test_size=0.33, shuffle=True, random_state=42)
        X_anatomy_train = X_anatomy.iloc[train_idx]
        X_anatomy_validation = X_anatomy.iloc[validation_idx]
        X_connectome_train = X_connectome.iloc[train_idx]
        X_connectome_validation = X_connectome.iloc[validation_idx]
        y_train = y[train_idx]
        y_validation = y[validation_idx]

        self.clf_connectome.fit(X_connectome_train, y_train)
        self.clf_anatomy.fit(X_anatomy_train, y_train)

        y_connectome_pred = self.clf_connectome.predict_proba(
            X_connectome_validation)
        y_anatomy_pred = self.clf_anatomy.predict_proba(X_anatomy_validation)

        self.meta_clf.fit(
            np.concatenate([y_connectome_pred, y_anatomy_pred], axis=1),
            y_validation)
        return self

    def predict(self, X):
        X_anatomy = X[[col for col in X.columns if col.startswith('anatomy')]]
        X_connectome = X[[
            col for col in X.columns if col.startswith('connectome')
        ]]

        y_anatomy_pred = self.clf_anatomy.predict_proba(X_anatomy)
        y_connectome_pred = self.clf_connectome.predict_proba(X_connectome)

        return self.meta_clf.predict(
            np.concatenate([y_connectome_pred, y_anatomy_pred], axis=1))

    def predict_proba(self, X):
        X_anatomy = X[[col for col in X.columns if col.startswith('anatomy')]]
        X_connectome = X[[
            col for col in X.columns if col.startswith('connectome')
        ]]

        y_anatomy_pred = self.clf_anatomy.predict_proba(X_anatomy)
        y_connectome_pred = self.clf_connectome.predict_proba(X_connectome)

        return self.meta_clf.predict_proba(
            np.concatenate([y_connectome_pred, y_anatomy_pred], axis=1))
