import numpy as np
import pandas as pd
from sklearn import decomposition

from sklearn.base import BaseEstimator
from sklearn.feature_selection import SelectKBest
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split


class Classifier(BaseEstimator):
    def __init__(self):
        test_weights = {0: 0.5892323030907278, 1: 0.4107676969092722}
        self.clf = LogisticRegression(
            C=0.1,
            tol=2,
            verbose=2,
            penalty='l2',
            class_weight=test_weights,
            solver="liblinear")

    def fit(self, X, y):
        selected = X[((X['anatomy_select'] == 1) |
                      (X['fmri_select'] == 1))].index.values
        y = pd.Series(y, index=X.index)
        y = y.loc[selected]
        X = X.loc[selected].drop(['anatomy_select', 'fmri_select'], axis=1)
        self.clf.fit(X, y)
        return self

    def predict(self, X):
        X = X.drop(['anatomy_select', 'fmri_select'], axis=1)
        return self.clf.predict(X)

    def predict_proba(self, X):
        X = X.drop(['anatomy_select', 'fmri_select'], axis=1)
        return self.clf.predict_proba(X)
