import numpy as np

from sklearn.base import BaseEstimator
from sklearn.svm import SVC
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import GridSearchCV

ATLAS = ('basc064', 'harvard_oxford_cort_prob_2mm', 'msdl', 'basc122')


class Classifier(BaseEstimator):
    def __init__(self):
        self.base_clf_dict = {key: SVC(probability=True) for key in ATLAS}
        self.clf = LogisticRegression(C=1.)
        self.svc_parameters = [{
            'kernel': ['rbf'],
            'gamma': [1e-3, 1e-4],
            'C': [0.5, 1, 10, 100, 1000]
        }, {
            'kernel': ['linear'],
            'C': [0.5, 1, 10, 100, 1000]
        }]

    def _clf_data(self, X):
        X_atlas_dict = {
            key: X[[col for col in X.columns if col.startswith(key)]].values
            for key in ATLAS
        }
        X_meta_clf = None
        for key in self.base_clf_dict.keys():
            base_predict_pro = self.base_clf_dict[key].predict_proba(
                X_atlas_dict[key])

            if X_meta_clf is None:
                X_meta_clf = base_predict_pro
            else:
                X_meta_clf = np.concatenate([X_meta_clf, base_predict_pro],
                                            axis=1)

        return X_meta_clf

    def _grid_search(self, estimator, parameters, X, y):
        grid_search = GridSearchCV(estimator, parameters, n_jobs=-1, verbose=1)
        grid_search.fit(X, y)

        return grid_search.best_params_

    def fit(self, X, y):
        X_atlas_dict = {
            key: X[[col for col in X.columns if col.startswith(key)]].values
            for key in ATLAS
        }
        for key, val in X_atlas_dict.items():
            best_params = self._grid_search(self.base_clf_dict[key],
                                            self.svc_parameters, val, y)
            self.base_clf_dict[key].set_params(**best_params)

            self.base_clf_dict[key].fit(val, y)

        X_clf = self._clf_data(X)
        self.clf.fit(X_clf, y)

        return self

    def predict(self, X):
        X_clf = self._clf_data(X)

        return self.clf.predict(X_clf)

    def predict_proba(self, X):
        X_clf = self._clf_data(X)

        return self.clf.predict_proba(X_clf)
