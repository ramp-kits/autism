from sklearn.base import BaseEstimator
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline


class Classifier(BaseEstimator):
    def __init__(self):
        self.clf = make_pipeline(StandardScaler(), LogisticRegression(C=0.01))

    def fit(self, X, y):
        self.clf.fit(X, y)
        return self

    def predict(self, X, y):
        return self.clf.predict(X)

    def predict_proba(self, X):
        return self.clf.predict_proba(X)
