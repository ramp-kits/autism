import os

import pandas as pd
import rampwf as rw

from sklearn.model_selection import StratifiedShuffleSplit

problem_title = 'Autism Spectrum Disorder classification'

_target_column_name = 'asd'
_prediction_label_names = [0, 1]

Predictions = rw.prediction_types.make_multiclass(
    label_names=_prediction_label_names)

workflow = rw.workflows.FeatureExtractorClassifier()

score_types = [
    rw.score_types.ROCAUC(name='auc', precision=3),
    rw.score_types.Accuracy(name='acc', precision=3),
]


def get_cv(X, y):
    cv = StratifiedShuffleSplit(n_splits=8, test_size=0.2, random_state=42)
    return cv.split(X, y)


def _read_data(path, filename):
    subject_id = pd.read_csv(os.path.join(path, 'data', filename), header=None)
    # read the list of the subjects
    df_participants = pd.read_csv(os.path.join(path, 'data',
                                               'participants.csv'),
                                  index_col=0)
    df_participants.columns = ['participants_' + col
                               for col in df_participants.columns]
    # load the structural and functional MRI data
    df_anatomy = pd.read_csv(os.path.join(path, 'data', 'anatomy.csv'),
                             index_col=0)
    df_anatomy.columns = ['anatomy_' + col
                          for col in df_anatomy.columns]
    df_fmri = pd.read_csv(os.path.join(path, 'data', 'fmri_filename.csv'),
                          index_col=0)
    df_fmri.columns = ['fmri_' + col
                       for col in df_fmri.columns]
    # load the QC for structural and functional MRI data
    df_anatomy_qc = pd.read_csv(os.path.join(path, 'data', 'anatomy_qc.csv'),
                                index_col=0)
    df_fmri_qc = pd.read_csv(os.path.join(path, 'data', 'fmri_qc.csv'),
                             index_col=0)
    df_fmri_tr = pd.read_csv(os.path.join(path, 'data',
                                          'fmri_repetition_time.csv'),
                             index_col=0)
    # rename the columns for the QC to have distinct names
    df_anatomy_qc = df_anatomy_qc.rename(columns={"select": "anatomy_select"})
    df_fmri_qc = df_fmri_qc.rename(columns={"select": "fmri_select"})

    X = pd.concat([df_participants, df_anatomy, df_anatomy_qc, df_fmri,
                   df_fmri_qc, df_fmri_tr], axis=1)
    X = X.loc[subject_id[0]]
    y = X['participants_asd']
    X = X.drop('participants_asd', axis=1)

    return X, y.values


def get_train_data(path='.'):
    filename = 'train.csv'
    return _read_data(path, filename)


def get_test_data(path='.'):
    filename = 'test.csv'
    return _read_data(path, filename)
