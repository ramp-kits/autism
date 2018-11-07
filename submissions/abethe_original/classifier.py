import numpy as np

from sklearn.base import BaseEstimator
from sklearn.preprocessing import StandardScaler, Normalizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import train_test_split


class Classifier(BaseEstimator):
    def __init__(self):
        self.clf_connectome_msdl = make_pipeline(
            StandardScaler(),
            LogisticRegression(
                C=8e-4, random_state=42, dual=False, penalty="l2"))
        self.clf_connectome_power = LogisticRegression(
            C=0.1, dual=True, penalty="l2", random_state=42)
        self.clf_connectome_harvard = LogisticRegression(
            C=0.1, dual=True, penalty="l2", random_state=42)
        self.clf_connectome_craddock = make_pipeline(
            StandardScaler(),
            LogisticRegression(
                C=5e-5, random_state=42, dual=False, penalty="l2"))
        self.clf_connectome_basc197 = make_pipeline(
            StandardScaler(),
            LogisticRegression(
                C=5e-5, random_state=42, dual=False, penalty="l2"))
        self.clf_connectome_basc122 = make_pipeline(
            StandardScaler(),
            LogisticRegression(
                C=0.0006, dual=False, penalty="l2", random_state=42))
        self.clf_connectome_basc064 = make_pipeline(
            Normalizer(norm="max"),
            LogisticRegression(
                C=0.01, dual=True, penalty="l2", tol=0.01, random_state=42))
        self.clf_anatomy = make_pipeline(
            StandardScaler(),
            LogisticRegression(C=0.008, random_state=42, penalty="l2"))
        self.meta_clf = make_pipeline(
            StandardScaler(),
            LogisticRegression(C=0.012, random_state=42, penalty="l2"))

    def fit(self, X, y):
        X_anatomy = X[[
            col for col in X.columns
            if (col.startswith('anatomy') | col.startswith('participant_sex'))
        ]]
        X_connectome_msdl = X[[
            col for col in X.columns if col.startswith('connectome_msdl')
        ]]
        X_connectome_power = X[[
            col for col in X.columns if col.startswith('connectome_power')
        ]]
        X_connectome_harvard = X[[
            col for col in X.columns if col.startswith('connectome_harvard')
        ]]
        X_connectome_craddock = X[[
            col for col in X.columns if col.startswith('connectome_craddock')
        ]]
        X_connectome_basc197 = X[[
            col for col in X.columns if col.startswith('connectome_basc197')
        ]]
        X_connectome_basc122 = X[[
            col for col in X.columns if col.startswith('connectome_basc122')
        ]]
        X_connectome_basc064 = X[[
            col for col in X.columns if col.startswith('connectome_basc064')
        ]]

        train_idx, validation_idx = train_test_split(
            range(y.size), test_size=0.33, shuffle=True, random_state=42)
        X_anatomy_train = X_anatomy.iloc[train_idx]
        X_anatomy_validation = X_anatomy.iloc[validation_idx]
        X_connectome_msdl_train = X_connectome_msdl.iloc[train_idx]
        X_connectome_msdl_validation = X_connectome_msdl.iloc[validation_idx]
        X_connectome_power_train = X_connectome_power.iloc[train_idx]
        X_connectome_power_validation = X_connectome_power.iloc[validation_idx]
        X_connectome_harvard_train = X_connectome_harvard.iloc[train_idx]
        X_connectome_harvard_validation = X_connectome_harvard.iloc[
            validation_idx]
        X_connectome_craddock_train = X_connectome_craddock.iloc[train_idx]
        X_connectome_craddock_validation = X_connectome_craddock.iloc[
            validation_idx]
        X_connectome_basc197_train = X_connectome_basc197.iloc[train_idx]
        X_connectome_basc197_validation = X_connectome_basc197.iloc[
            validation_idx]
        X_connectome_basc122_train = X_connectome_basc122.iloc[train_idx]
        X_connectome_basc122_validation = X_connectome_basc122.iloc[
            validation_idx]
        X_connectome_basc064_train = X_connectome_basc064.iloc[train_idx]
        X_connectome_basc064_validation = X_connectome_basc064.iloc[
            validation_idx]
        y_train = y[train_idx]
        y_validation = y[validation_idx]

        self.clf_connectome_msdl.fit(X_connectome_msdl_train, y_train)
        self.clf_connectome_power.fit(X_connectome_power_train, y_train)
        self.clf_connectome_harvard.fit(X_connectome_harvard_train, y_train)
        self.clf_connectome_craddock.fit(X_connectome_craddock_train, y_train)
        self.clf_connectome_basc197.fit(X_connectome_basc197_train, y_train)
        self.clf_connectome_basc122.fit(X_connectome_basc122_train, y_train)
        self.clf_connectome_basc064.fit(X_connectome_basc064_train, y_train)
        self.clf_anatomy.fit(X_anatomy_train, y_train)

        y_connectome_msdl_pred = self.clf_connectome_msdl.predict_proba(
            X_connectome_msdl_validation)
        y_connectome_power_pred = self.clf_connectome_power.predict_proba(
            X_connectome_power_validation)
        y_connectome_harvard_pred = self.clf_connectome_harvard.predict_proba(
            X_connectome_harvard_validation)
        y_connectome_craddock_pred = self.clf_connectome_craddock.predict_proba(
            X_connectome_craddock_validation)
        y_connectome_basc197_pred = self.clf_connectome_basc197.predict_proba(
            X_connectome_basc197_validation)
        y_connectome_basc122_pred = self.clf_connectome_basc122.predict_proba(
            X_connectome_basc122_validation)
        y_connectome_basc064_pred = self.clf_connectome_basc064.predict_proba(
            X_connectome_basc064_validation)
        y_anatomy_pred = self.clf_anatomy.predict_proba(X_anatomy_validation)

        self.meta_clf.fit(
            np.concatenate([
                y_connectome_msdl_pred, y_connectome_power_pred,
                y_connectome_harvard_pred, y_connectome_craddock_pred,
                y_connectome_basc197_pred, y_connectome_basc122_pred,
                y_connectome_basc064_pred, y_anatomy_pred
            ],
                           axis=1), y_validation)
        return self

    def predict(self, X):
        X_anatomy = X[[
            col for col in X.columns
            if (col.startswith('anatomy') | col.startswith('participant_sex'))
        ]]

        X_connectome_msdl = X[[
            col for col in X.columns if col.startswith('connectome_msdl')
        ]]
        X_connectome_power = X[[
            col for col in X.columns if col.startswith('connectome_power')
        ]]
        X_connectome_harvard = X[[
            col for col in X.columns if col.startswith('connectome_harvard')
        ]]
        X_connectome_craddock = X[[
            col for col in X.columns if col.startswith('connectome_craddock')
        ]]
        X_connectome_basc197 = X[[
            col for col in X.columns if col.startswith('connectome_basc197')
        ]]
        X_connectome_basc122 = X[[
            col for col in X.columns if col.startswith('connectome_basc122')
        ]]
        X_connectome_basc064 = X[[
            col for col in X.columns if col.startswith('connectome_basc064')
        ]]

        y_anatomy_pred = self.clf_anatomy.predict_proba(X_anatomy)
        y_connectome_msdl_pred = self.clf_connectome_msdl.predict_proba(
            X_connectome_msdl)
        y_connectome_power_pred = self.clf_connectome_power.predict_proba(
            X_connectome_power)
        y_connectome_harvard_pred = self.clf_connectome_harvard.predict_proba(
            X_connectome_harvard)
        y_connectome_craddock_pred = self.clf_connectome_craddock.predict_proba(
            X_connectome_craddock)
        y_connectome_basc197_pred = self.clf_connectome_basc197.predict_proba(
            X_connectome_basc197)
        y_connectome_basc122_pred = self.clf_connectome_basc122.predict_proba(
            X_connectome_basc122)
        y_connectome_basc064_pred = self.clf_connectome_basc064.predict_proba(
            X_connectome_basc064)

        return self.meta_clf.predict(
            np.concatenate([
                y_connectome_msdl_pred, y_connectome_power_pred,
                y_connectome_harvard_pred, y_connectome_craddock_pred,
                y_connectome_basc197_pred, y_connectome_basc122_pred,
                y_connectome_basc064_pred, y_anatomy_pred
            ],
                           axis=1))

    def predict_proba(self, X):
        X_anatomy = X[[
            col for col in X.columns
            if (col.startswith('anatomy') | col.startswith('participant_sex'))
        ]]
        X_connectome_msdl = X[[
            col for col in X.columns if col.startswith('connectome_msdl')
        ]]
        X_connectome_power = X[[
            col for col in X.columns if col.startswith('connectome_power')
        ]]
        X_connectome_harvard = X[[
            col for col in X.columns if col.startswith('connectome_harvard')
        ]]
        X_connectome_craddock = X[[
            col for col in X.columns if col.startswith('connectome_craddock')
        ]]
        X_connectome_basc197 = X[[
            col for col in X.columns if col.startswith('connectome_basc197')
        ]]
        X_connectome_basc122 = X[[
            col for col in X.columns if col.startswith('connectome_basc122')
        ]]
        X_connectome_basc064 = X[[
            col for col in X.columns if col.startswith('connectome_basc064')
        ]]

        y_anatomy_pred = self.clf_anatomy.predict_proba(X_anatomy)
        y_connectome_msdl_pred = self.clf_connectome_msdl.predict_proba(
            X_connectome_msdl)
        y_connectome_power_pred = self.clf_connectome_power.predict_proba(
            X_connectome_power)
        y_connectome_harvard_pred = self.clf_connectome_harvard.predict_proba(
            X_connectome_harvard)
        y_connectome_craddock_pred = self.clf_connectome_craddock.predict_proba(
            X_connectome_craddock)
        y_connectome_basc197_pred = self.clf_connectome_basc197.predict_proba(
            X_connectome_basc197)
        y_connectome_basc122_pred = self.clf_connectome_basc122.predict_proba(
            X_connectome_basc122)
        y_connectome_basc064_pred = self.clf_connectome_basc064.predict_proba(
            X_connectome_basc064)

        return self.meta_clf.predict_proba(
            np.concatenate([
                y_connectome_msdl_pred, y_connectome_power_pred,
                y_connectome_harvard_pred, y_connectome_craddock_pred,
                y_connectome_basc197_pred, y_connectome_basc122_pred,
                y_connectome_basc064_pred, y_anatomy_pred
            ],
                           axis=1))
