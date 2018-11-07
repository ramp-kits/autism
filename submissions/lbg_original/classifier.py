import numpy as np

from sklearn.base import BaseEstimator
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import BaggingClassifier

from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras.layers import Conv1D, GlobalAveragePooling1D

np.random.seed(42)


def _preprocess_data(data, labels=None, nsubseq=5, maxlen=40):
    nfeat = data[0].shape[1]
    data_aug = []
    labels_aug = []
    for k in range(len(data)):
        seq_lenth_tmp = data[k].shape[0]
        if seq_lenth_tmp < (maxlen + nsubseq - 1):
            data_padded_tmp = np.zeros((maxlen + nsubseq - 1, nfeat))
            data_padded_tmp[-seq_lenth_tmp:] = data[k]
            ind_tmp = np.linspace(0, nsubseq - 1, nsubseq).astype(int)
            for i in ind_tmp:
                data_aug.append(data_padded_tmp[i:(i + maxlen)])
                if labels is not None:
                    labels_aug.append(labels[k])
        else:
            ind_tmp = np.linspace(0, seq_lenth_tmp - maxlen,
                                  nsubseq).astype(int)
            for i in ind_tmp:
                data_aug.append(data[k][i:(i + maxlen)])
                if labels is not None:
                    labels_aug.append(labels[k])
    if labels is not None:
        return np.array(data_aug), np.array(labels_aug)
    else:
        return np.array(data_aug)


class ConvClassifier(BaseEstimator):
    def __init__(self, nhid=64, epochs=10, nsubseq=5, maxlen=50,
                 kernel_size=3):
        self.nhid = nhid
        self.epochs = epochs
        self.nsubseq = nsubseq
        self.maxlen = maxlen
        self.kernel_size = kernel_size
        self.model_ = None

    def fit(self, X, y, **kwargs):
        self.set_params(**kwargs)
        nfeat = X[0].shape[1]
        model = Sequential()
        model.add(
            Conv1D(
                self.nhid,
                self.kernel_size,
                activation='relu',
                input_shape=(self.maxlen, nfeat)))
        model.add(Dropout(0.4))
        model.add(GlobalAveragePooling1D())
        model.add(Dense(1, activation='sigmoid'))
        model.compile(
            loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])
        X_train, y_train = _preprocess_data(
            data=X, labels=y, nsubseq=self.nsubseq, maxlen=self.maxlen)
        model.fit(
            X_train,
            y_train,
            epochs=self.epochs,
            batch_size=32,
            verbose=0,
            shuffle=True)
        self.model_ = model
        return self

    def predict(self, X):
        X_test = _preprocess_data(
            data=X, nsubseq=self.nsubseq, maxlen=self.maxlen)
        y_pred = self.model_.predict(X_test)
        probs = np.mean(
            np.reshape(y_pred, (-1, self.nsubseq)), axis=1, keepdims=True)
        return (probs > 0.5).astype('int32')

    def predict_proba(self, X):
        X_test = _preprocess_data(
            data=X, nsubseq=self.nsubseq, maxlen=self.maxlen)
        y_pred = self.model_.predict(X_test)
        probs = np.mean(
            np.reshape(y_pred, (-1, self.nsubseq)), axis=1, keepdims=True)
        probs = np.hstack([1 - probs, probs])
        return probs


class Classifier(BaseEstimator):
    def __init__(self):
        self.clf_anat = make_pipeline(
            StandardScaler(),
            BaggingClassifier(
                base_estimator=LogisticRegression(C=0.5),
                n_estimators=50,
                max_samples=0.8,
                max_features=0.8,
                random_state=42))
        self.clf_fc1 = make_pipeline(
            StandardScaler(),
            BaggingClassifier(
                base_estimator=LogisticRegression(C=0.5),
                n_estimators=50,
                max_samples=0.8,
                max_features=0.8,
                random_state=42))
        self.clf_fc2 = make_pipeline(
            StandardScaler(),
            BaggingClassifier(
                base_estimator=LogisticRegression(C=0.5),
                n_estimators=50,
                max_samples=0.8,
                max_features=0.8,
                random_state=42))
        self.clf_nn1 = ConvClassifier()
        self.clf_nn2 = ConvClassifier(nhid=32, epochs=5, nsubseq=10, maxlen=70)

        self.meta_clf = make_pipeline(StandardScaler(), LogisticRegression())

    def fit(self, X, y):
        X_anat = X[[col for col in X.columns if col.startswith('anatomy')]]
        X_fc1 = X[[col for col in X.columns if col.startswith('fc1')]]
        X_fc2 = X[[col for col in X.columns if col.startswith('fc2')]]
        X_nn1 = np.array(X.nn1)
        X_nn2 = np.array(X.nn2)

        cv = StratifiedKFold(n_splits=8, shuffle=True, random_state=42)
        y_pred = []
        y_val = []
        for train_idx, validation_idx in cv.split(X, y):
            X_anat_train = X_anat.iloc[train_idx]
            X_anat_validation = X_anat.iloc[validation_idx]
            X_fc1_train = X_fc1.iloc[train_idx]
            X_fc1_validation = X_fc1.iloc[validation_idx]
            X_fc2_train = X_fc2.iloc[train_idx]
            X_fc2_validation = X_fc2.iloc[validation_idx]
            X_nn1_train = X_nn1[train_idx]
            X_nn1_validation = X_nn1[validation_idx]
            X_nn2_train = X_nn2[train_idx]
            X_nn2_validation = X_nn2[validation_idx]

            y_train = y[train_idx]
            y_validation = y[validation_idx]

            self.clf_anat.fit(X_anat_train, y_train)
            self.clf_fc1.fit(X_fc1_train, y_train)
            self.clf_fc2.fit(X_fc2_train, y_train)
            self.clf_nn1.fit(X_nn1_train, y_train)
            self.clf_nn2.fit(X_nn2_train, y_train)

            y_anat_pred = self.clf_anat.predict_proba(
                X_anat_validation)[:, 0].reshape(-1, 1)
            y_fc1_pred = self.clf_fc1.predict_proba(
                X_fc1_validation)[:, 0].reshape(-1, 1)
            y_fc2_pred = self.clf_fc2.predict_proba(
                X_fc2_validation)[:, 0].reshape(-1, 1)
            y_nn1_pred = self.clf_nn1.predict_proba(
                X_nn1_validation)[:, 0].reshape(-1, 1)
            y_nn2_pred = self.clf_nn2.predict_proba(
                X_nn2_validation)[:, 0].reshape(-1, 1)

            y_pred.extend(
                np.concatenate([
                    y_anat_pred, y_fc1_pred, y_fc2_pred, y_nn1_pred,
                    y_nn2_pred, y_anat_pred * y_fc1_pred,
                    y_anat_pred * y_nn1_pred, y_fc2_pred * y_nn2_pred
                ],
                               axis=1))
            y_val.extend(y_validation)

        self.clf_anat.fit(X_anat, y)
        self.clf_fc1.fit(X_fc1, y)
        self.clf_fc2.fit(X_fc2, y)
        self.clf_nn1.fit(X_nn1, y)
        self.clf_nn2.fit(X_nn2, y)

        self.meta_clf.fit(y_pred, y_val)
        return self

    def predict(self, X):
        X_anat = X[[col for col in X.columns if col.startswith('anatomy')]]
        X_fc1 = X[[col for col in X.columns if col.startswith('fc1')]]
        X_fc2 = X[[col for col in X.columns if col.startswith('fc2')]]
        X_nn1 = np.array(X.nn1)
        X_nn2 = np.array(X.nn2)

        y_anat_pred = self.clf_anat.predict_proba(X_anat)[:, 0].reshape(-1, 1)
        y_fc1_pred = self.clf_fc1.predict_proba(X_fc1)[:, 0].reshape(-1, 1)
        y_fc2_pred = self.clf_fc2.predict_proba(X_fc2)[:, 0].reshape(-1, 1)
        y_nn1_pred = self.clf_nn1.predict_proba(X_nn1)[:, 0].reshape(-1, 1)
        y_nn2_pred = self.clf_nn2.predict_proba(X_nn2)[:, 0].reshape(-1, 1)

        return self.meta_clf.predict(
            np.concatenate([
                y_anat_pred, y_fc1_pred, y_fc2_pred, y_nn1_pred, y_nn2_pred,
                y_anat_pred * y_fc1_pred, y_anat_pred * y_nn1_pred,
                y_fc2_pred * y_nn2_pred
            ],
                           axis=1))

    def predict_proba(self, X):
        X_anat = X[[col for col in X.columns if col.startswith('anatomy')]]
        X_fc1 = X[[col for col in X.columns if col.startswith('fc1')]]
        X_fc2 = X[[col for col in X.columns if col.startswith('fc2')]]
        X_nn1 = np.array(X.nn1)
        X_nn2 = np.array(X.nn2)

        y_anat_pred = self.clf_anat.predict_proba(X_anat)[:, 0].reshape(-1, 1)
        y_fc1_pred = self.clf_fc1.predict_proba(X_fc1)[:, 0].reshape(-1, 1)
        y_fc2_pred = self.clf_fc2.predict_proba(X_fc2)[:, 0].reshape(-1, 1)
        y_nn1_pred = self.clf_nn1.predict_proba(X_nn1)[:, 0].reshape(-1, 1)
        y_nn2_pred = self.clf_nn2.predict_proba(X_nn2)[:, 0].reshape(-1, 1)

        return self.meta_clf.predict_proba(
            np.concatenate([
                y_anat_pred, y_fc1_pred, y_fc2_pred, y_nn1_pred, y_nn2_pred,
                y_anat_pred * y_fc1_pred, y_anat_pred * y_nn1_pred,
                y_fc2_pred * y_nn2_pred
            ],
                           axis=1))
