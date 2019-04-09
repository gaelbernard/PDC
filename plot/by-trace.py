from Log import Log
import pandas as pd
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer
import matplotlib.pyplot as plt
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import AgglomerativeClustering
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import sys
import random

np.set_printoptions(threshold=sys.maxsize)
pd.options.display.max_columns = 1000
pd.options.display.max_rows = 1000
pd.options.display.max_colwidth = 199
pd.options.display.width = None

from sklearn.metrics import pairwise_distances


def get_feature4(log):

    # Distance in next neighboors
    data = defaultdict(list)
    for i in log.vector_activities.index:
        for win in [1,6]:
            data['left_{}'.format(win)].append('$'.join(log.lefts[i][-win:]))
            data['right_{}'.format(win)].append('$'.join(log.rights[i][:win]))
            data['left_right_{}'.format(win)].append('$'.join(log.rights[i][:win]+[log.vector_activities[i]]+log.lefts[i][-win:]))
    f = []
    for txt in data.values():
        cv = CountVectorizer(ngram_range=(1,1), token_pattern='[^$]+', binary=False)
        data = cv.fit_transform(txt)
        f.append(pd.DataFrame(data.toarray(), columns=cv.get_feature_names()))
    f = pd.concat(f, axis=1)
    dists_neigh = pairwise_distances(f, metric='cosine')
    if dists_neigh.max().max()!=0:
        dists_neigh = dists_neigh/dists_neigh.max().max()

    # Distance activity seen before or after
    results = {}
    for i in log.vector_activities.index:
        results[i] = {}
        for l in log.alphabet:
            is_before = l in log.lefts[i]
            is_after = l in log.lefts[i]
            if is_after and is_after:
                v = 3
            elif is_after:
                v = 2
            elif is_before:
                v = 1
            else:
                v = 0
            results[i][l] = v

    dists_b_a = pd.DataFrame(results).T
    dists_b_a = pairwise_distances(dists_b_a, metric='hamming')

    dists = (dists_b_a+dists_neigh)/2
    return dists


for i in range(1,11):
    dataset = 'log{}-training'.format(i)

    # Load Logs
    log = Log()
    log.read_csv('/Users/gbernar1/Desktop/pdc_3/PDC_repo/data/{}.csv'.format(dataset))

    feature = get_feature4(log)
    feature = pd.DataFrame(feature)

    svd = pd.DataFrame(TruncatedSVD(n_components=2).fit_transform(feature))
    axis_coord = (svd[0].min().min(),svd[0].max().max(), svd[1].min().min(),svd[1].max().max())

    # By case
    svd['case'] = log.vector_traces
    sub_svd = svd.groupby('case').mean()
    plt.scatter(sub_svd[0], sub_svd[1])
    plt.axis(axis_coord)
    plt.title('{}: trace'.format(dataset))
    plt.savefig('trace/{}.png'.format(dataset))
    plt.close()
    svd.drop(['case'], axis=1, inplace=True)
    del sub_svd

    # By activity
    svd['activity'] = log.vector_activities
    sub_svd = svd.groupby('activity').mean()
    plt.figure(figsize=(20,10))
    plt.scatter(sub_svd[0], sub_svd[1], s=0)
    for i, txt in enumerate(log.vector_activities.unique()):
        r = random.uniform(-2, 2)
        plt.annotate(txt, (sub_svd[0][i]+r, sub_svd[1][i]+r))
    plt.axis(axis_coord)
    plt.title('{}: activity'.format(dataset))
    plt.savefig('activity/{}.png'.format(dataset))
    plt.close()
    svd.drop(['activity'], axis=1, inplace=True)


    # By letter
    for activity in log.vector_activities.unique():
        if activity in ['LEFT-padding', 'RIGHT-padding']:
            continue
        sub_svd = svd.loc[log.vector_activities==activity, :]

        plt.figure(figsize=(20,10))
        plt.scatter(sub_svd[0], sub_svd[1])
        plt.axis(axis_coord)
        plt.title('{}: letter:{}'.format(dataset, activity))
        plt.savefig('alphabet/{}_{}.png'.format(dataset, activity))
        plt.close()


