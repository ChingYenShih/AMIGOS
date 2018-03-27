#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
Affective Computing with AMIGOS Dataset
'''

from argparse import ArgumentParser
import os
import time
import matplotlib.pyplot as plt
import numpy as np
from sklearn.naive_bayes import GaussianNB
from sklearn.svm import SVC
from sklearn.model_selection import KFold
from sklearn.metrics import accuracy_score, f1_score
import xgboost as xgb

from config import MISSING_DATA_SUBJECT, SUBJECT_NUM, VIDEO_NUM, FEATURE_NAMES


def main():
    ''' Main function '''
    parser = ArgumentParser(
        description='Affective Computing with AMIGOS Dataset -- Cross Validation')
    parser.add_argument('--data', type=str, default='./data')
    parser.add_argument('--feat', type=str, choices=['eeg', 'ecg', 'gsr', 'all'],
                        default='all', help='choose type of modality')
    parser.add_argument('--clf', type=str, choices=['gnb', 'svm', 'xgb'],
                        default='xgb', help='choose type of classifier')
    parser.add_argument('--nor', type=str, choices=['one', 'mean', 'no'],
                        default='no', help='choose type of classifier')
    parser.add_argument('--new', action='store_true')
    args = parser.parse_args()

    # read extracted features
    if args.new:
        amigos_data = np.loadtxt(os.path.join(args.data, 'mse_pe_features.csv'), delimiter=',')
    else:
        amigos_data = np.loadtxt(os.path.join(args.data, 'features.csv'), delimiter=',')

    # read labels and split to 0 and 1 by
    labels = np.loadtxt(os.path.join(args.data, 'label.csv'), delimiter=',')
    labels = labels[:, :2]
    a_labels, v_labels = [], []
    for i in range(SUBJECT_NUM):
        if i + 1 in MISSING_DATA_SUBJECT:
            continue
        a_labels_mean = np.mean(labels[i * VIDEO_NUM:i * VIDEO_NUM + VIDEO_NUM, 0])
        v_labels_mean = np.mean(labels[i * VIDEO_NUM:i * VIDEO_NUM + VIDEO_NUM, 1])
        for idx, label in enumerate(labels[i * VIDEO_NUM:i * VIDEO_NUM + VIDEO_NUM, :]):
            a_tmp = 1 if label[0] > a_labels_mean else 0
            v_tmp = 1 if label[1] > v_labels_mean else 0
            a_labels.append(a_tmp)
            v_labels.append(v_tmp)
    a_labels, v_labels = np.array(a_labels), np.array(v_labels)

    # setup kfold cross validator
    sub_num = SUBJECT_NUM - len(MISSING_DATA_SUBJECT)
    kf = KFold(n_splits=sub_num)

    # tune classifier parameters
    tuning_params = np.arange(1, 101, 1)
    a_acc_history = []
    v_acc_history = []

    for param in tuning_params:
        # setup classifier
        if args.clf == 'gnb':
            a_clf = GaussianNB()
            v_clf = GaussianNB()
        elif args.clf == 'svm':
            a_clf = SVC(C=0.9, kernel='linear')
            v_clf = SVC(C=0.3, kernel='linear')
        elif args.clf == 'xgb':
            a_clf = xgb.XGBClassifier(
                max_depth=1,
                learning_rate=.1,
                n_estimators=param,
                silent=True,
                objective="binary:logistic",
                nthread=-1,
                gamma=0,
                min_child_weight=1,
                max_delta_step=0,
                subsample=1,
                colsample_bytree=1,
                colsample_bylevel=1,
                reg_alpha=0,
                reg_lambda=1,
                scale_pos_weight=1,
                base_score=.5,
                seed=0
            )
            v_clf = xgb.XGBClassifier(
                max_depth=1,
                learning_rate=.1,
                n_estimators=param,
                silent=True,
                objective="binary:logistic",
                nthread=-1,
                gamma=0,
                min_child_weight=1,
                max_delta_step=0,
                subsample=1,
                colsample_bytree=1,
                colsample_bylevel=1,
                reg_alpha=0,
                reg_lambda=1,
                scale_pos_weight=1,
                base_score=.5,
                seed=0
            )

        # initialize history list
        train_a_accuracy_history = []
        train_v_accuracy_history = []
        train_a_f1score_history = []
        train_v_f1score_history = []
        val_a_accuracy_history = []
        val_v_accuracy_history = []
        val_a_f1score_history = []
        val_v_f1score_history = []

        # a_imps = np.zeros((sub_num, len(FEATURE_NAMES)))
        # v_imps = np.zeros((sub_num, len(FEATURE_NAMES)))

        start_time = time.time()

        for idx, (train_idx, val_idx) in enumerate(kf.split(amigos_data)):
            print(idx + 1, 'Fold Start')

            # collect data for cross validation
            if args.feat == 'eeg':
                train_data, val_data = amigos_data[train_idx, :175], amigos_data[val_idx, :175]
                if args.new:
                    train_pe, val_pe = amigos_data[train_idx,
                                                   287:302], amigos_data[val_idx, 287:302]
                    train_data = np.hstack((train_data, train_pe))
                    val_data = np.hstack((val_data, val_pe))
            elif args.feat == 'ecg':
                train_data, val_data = amigos_data[train_idx,
                                                   175:256], amigos_data[val_idx, 175:256]
                if args.new:
                    train_pe, val_pe = amigos_data[train_idx,
                                                   302:317], amigos_data[val_idx, 302:317]
                    train_mse, val_mse = amigos_data[train_idx,
                                                     332:338], amigos_data[val_idx, 332:338]
                    train_data = np.hstack((train_data, train_pe, train_mse))
                    val_data = np.hstack((val_data, val_pe, val_mse))
            elif args.feat == 'gsr':
                train_data, val_data = amigos_data[train_idx,
                                                   256:287], amigos_data[val_idx, 256:287]
                if args.new:
                    train_pe, val_pe = amigos_data[train_idx,
                                                   317:332], amigos_data[val_idx, 317:332]
                    train_data = np.hstack((train_data, train_pe))
                    val_data = np.hstack((val_data, val_pe))
            elif args.feat == 'all':
                train_data, val_data = amigos_data[train_idx], amigos_data[val_idx]

            train_a_labels, val_a_labels = a_labels[train_idx], a_labels[val_idx]
            train_v_labels, val_v_labels = v_labels[train_idx], v_labels[val_idx]

            if args.nor == 'mean':
                # normalize using mean and std
                train_data_mean = np.mean(train_data, axis=0)
                train_data_std = np.std(train_data, axis=0)
                train_data = (train_data - train_data_mean) / train_data_std
                val_data_mean = np.mean(val_data, axis=0)
                val_data_std = np.std(val_data, axis=0)
                val_data = (val_data - val_data_mean) / val_data_std
            elif args.nor == 'one':
                # map features to [-1, 1]
                train_data_max = np.max(train_data, axis=0)
                train_data_min = np.min(train_data, axis=0)
                train_data = (train_data - train_data_min) / (train_data_max - train_data_min)
                train_data = train_data * 2 - 1
                val_data_max = np.max(val_data, axis=0)
                val_data_min = np.min(val_data, axis=0)
                val_data = (val_data - val_data_min) / (val_data_max - val_data_min)
                val_data = val_data * 2 - 1

            # fit classifier
            a_clf.fit(train_data, train_a_labels)
            v_clf.fit(train_data, train_v_labels)

            # a_imp = a_clf.get_booster().get_fscore()
            # a_tuples= [(k, a_imp[k]) for k in a_imp]
            # for i, (_, value) in enumerate(sorted(a_tuples, key=lambda x: int(x[0][1:]))):
            #     a_imps[idx][i] = value
            # v_imp = v_clf.get_booster().get_fscore()
            # v_tuples= [(k, v_imp[k]) for k in v_imp]
            # for i, (_, value) in enumerate(sorted(v_tuples, key=lambda x: int(x[0][1:]))):
            #     v_imps[idx][i] = value

            # predict arousal and valence
            train_a_predict_labels = a_clf.predict(train_data)
            train_v_predict_labels = v_clf.predict(train_data)
            val_a_predict_labels = a_clf.predict(val_data)
            val_v_predict_labels = v_clf.predict(val_data)

            # metrics calculation (accuracy and f1 score)
            train_a_accuracy = accuracy_score(train_a_labels, train_a_predict_labels)
            train_v_accuracy = accuracy_score(train_v_labels, train_v_predict_labels)
            train_a_f1score = f1_score(train_a_labels, train_a_predict_labels, average='macro')
            train_v_f1score = f1_score(train_v_labels, train_v_predict_labels, average='macro')
            val_a_accuracy = accuracy_score(val_a_labels, val_a_predict_labels)
            val_v_accuracy = accuracy_score(val_v_labels, val_v_predict_labels)
            val_a_f1score = f1_score(val_a_labels, val_a_predict_labels, average='macro')
            val_v_f1score = f1_score(val_v_labels, val_v_predict_labels, average='macro')

            train_a_accuracy_history.append(train_a_accuracy)
            train_v_accuracy_history.append(train_v_accuracy)
            train_a_f1score_history.append(train_a_f1score)
            train_v_f1score_history.append(train_v_f1score)
            val_a_accuracy_history.append(val_a_accuracy)
            val_v_accuracy_history.append(val_v_accuracy)
            val_a_f1score_history.append(val_a_f1score)
            val_v_f1score_history.append(val_v_f1score)

            print('Training Result')
            print("Arousal: Accuracy: {:.4f}, F1score: {:.4f}".format(
                train_a_accuracy, train_a_f1score))
            print("Valence: Accuracy: {:.4f}, F1score: {:.4f}".format(
                train_v_accuracy, train_v_f1score))

            print('Validating Result')
            print("Arousal: Accuracy: {:.4f}, F1score: {:.4f}".format(
                val_a_accuracy, val_a_f1score))
            print("Valence: Accuracy: {:.4f}, F1score: {:.4f}".format(
                val_v_accuracy, val_v_f1score))

        print('\nDone. Duration: ', time.time() - start_time)

        train_a_mean_accuracy = np.mean(train_a_accuracy_history)
        train_v_mean_accuracy = np.mean(train_v_accuracy_history)
        val_a_mean_accuracy = np.mean(val_a_accuracy_history)
        val_v_mean_accuracy = np.mean(val_v_accuracy_history)

        print('\nAverage Training Result')
        print("Arousal => Accuracy: {:.4f}, F1score: {:.4f}".format(
            train_a_mean_accuracy, np.mean(train_a_f1score_history)))
        print("Valence => Accuracy: {:.4f}, F1score: {:.4f}".format(
            train_v_mean_accuracy, np.mean(train_v_f1score_history)))

        print('Average Validating Result')
        print("Arousal => Accuracy: {:.4f}, F1score: {:.4f}".format(
            val_a_mean_accuracy, np.mean(val_a_f1score_history)))
        print("Valence => Accuracy: {:.4f}, F1score: {:.4f}".format(
            val_v_mean_accuracy, np.mean(val_v_f1score_history)))

        a_acc_history.append(val_a_mean_accuracy)
        v_acc_history.append(val_v_mean_accuracy)

    # print best parameter
    print()
    # print([float("{:.4f}".format(a)) for a in a_acc_history])
    a_max_idx = np.argmax(a_acc_history)
    a_min_idx = np.argmin(a_acc_history)
    print("Best value: {}, a_acc: {:.4f}".format(
        tuning_params[a_max_idx], a_acc_history[a_max_idx]))
    print("Best value: {}, a_acc: {:.4f}".format(
        tuning_params[a_min_idx], a_acc_history[a_min_idx]))

    print()
    # print([float("{:.4f}".format(a)) for a in v_acc_history])
    v_max_idx = np.argmax(v_acc_history)
    v_min_idx = np.argmin(v_acc_history)
    print("Best value: {}, v_acc: {:.4f}".format(
        tuning_params[v_max_idx], v_acc_history[v_max_idx]))
    print("Best value: {}, v_acc: {:.4f}".format(
        tuning_params[v_min_idx], v_acc_history[v_min_idx]))

    # a_imps = np.mean(a_imps, axis=0)
    # v_imps = np.mean(v_imps, axis=0)
    # a_imps_idx = np.argsort(a_imps)[::-1]
    # v_imps_idx = np.argsort(v_imps)[::-1]
    # a_imps = np.sort(a_imps)[::-1]
    # v_imps = np.sort(v_imps)[::-1]
    # a_imps_name = []
    # v_imps_name = []
    # for i in range(a_imps_idx.size):
    #     a_imps_name.append(FEATURE_NAMES[a_imps_idx[i]])
    #     v_imps_name.append(FEATURE_NAMES[v_imps_idx[i]])

    # max_num = 10
    # a_imps = a_imps[:max_num]
    # v_imps = v_imps[:max_num]
    # a_imps_name = a_imps_name[:max_num]
    # v_imps_name = v_imps_name[:max_num]

    # plt.bar(np.arange(a_imps.size), a_imps)
    # plt.title('Arousal Feature Importance')
    # plt.ylabel('F Score')
    # plt.xticks(np.arange(a_imps.size), a_imps_name)
    # plt.show()

    # plt.bar(np.arange(v_imps.size), v_imps)
    # plt.title('Valence Feature Importance')
    # plt.ylabel('F Score')
    # plt.xticks(np.arange(v_imps.size), v_imps_name)
    # plt.show()


if __name__ == '__main__':

    main()
