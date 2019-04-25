from Object.Log import Log
import pandas as pd
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.cluster import AgglomerativeClustering
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
import sys
import random
from sklearn.metrics import silhouette_score
np.set_printoptions(threshold=sys.maxsize)
pd.options.display.max_columns = 1000
pd.options.display.max_rows = 1000
pd.options.display.max_colwidth = 199
pd.options.display.width = None
from sklearn.cluster import AgglomerativeClustering
from sklearn.metrics import pairwise_distances
from sklearn.decomposition import TruncatedSVD
from pm4py.objects.log.adapters.pandas import csv_import_adapter
from pm4py.objects.conversion.log import factory as conversion_factory
from Object.Log import Log
from pm4py.algo.discovery.inductive import factory as inductive_miner
from pm4py.visualization.petrinet import factory as pn_vis_factory
import re
import pandas as pd
from pm4py.objects.petri import utils
import os
from pm4py.objects.petri.importer import pnml as pnml_importer
from pm4py.algo.conformance.alignments import factory as align_factory
from pm4py.algo.discovery.inductive import factory as inductive_miner
from anytree.exporter import JsonExporter


class Feature:

    def __init__(self):
        self.feature = {
            'distance_position': None,
            'distance_next_neigh': None,
            'distance_in_count_activity_before': None,
            'distance_in_activity_seen_before': None,
        }
        self.distanceMatrix = None

    def distance_position(self, log):
        self.feature['distance_position'] = np.array([position for seq_aligned in log.seq for position, e in enumerate(seq_aligned) if e!='-']).reshape(-1, 1)

    def distance_next_neigh(self, log, onlyLeft=False):
        data = defaultdict(list)
        for i in log.vector_activities.index:
            for win in [1,8]:
                data['left_{}'.format(win)].append('$'.join(log.lefts[i][-win:]))
                if not onlyLeft:
                    data['right_{}'.format(win)].append('$'.join(log.rights[i][:win]))
                    data['left_right_{}'.format(win)].append('$'.join(log.rights[i][:win]+[log.vector_activities[i]]+log.lefts[i][-win:]))
        f = []
        for txt in data.values():
            cv = CountVectorizer(ngram_range=(1,1), token_pattern='[^$]+', binary=False)
            data = cv.fit_transform(txt)
            f.append(pd.DataFrame(data.toarray(), columns=cv.get_feature_names()))
        f = pd.concat(f, axis=1)
        self.feature['distance_next_neigh'] =  f

    def distance_in_count_activity_before(self, log):
        d = []
        for i in log.vector_activities.index:
            d.append(log.lefts[i].count(log.vector_activities[i]))
        self.feature['distance_in_count_activity_before'] =  np.array(d).reshape(-1, 1)

    def distance_in_activity_seen_before(self, log):
        results = {}
        for i in log.vector_activities.index:
            results[i] = {}
            for l in log.alphabet:
                is_before = l in log.lefts[i]
                is_after = l in log.lefts[i]
                if is_after and is_before:
                    v = 3
                elif is_after:
                    v = 2
                elif is_before:
                    v = 1
                else:
                    v = 0
                results[i][l] = v

        self.feature['distance_in_activity_seen_before'] = pd.DataFrame(results).T

    def build_distanceMatrix(self, log):
        self.distance_position(log)
        self.distance_next_neigh(log)
        self.distance_in_count_activity_before(log)
        self.distance_in_activity_seen_before(log)
        self.get_distanceMatrix()

    def get_distanceMatrix(self):
        dists_position = pairwise_distances(self.feature['distance_position'], metric='manhattan')
        if dists_position.max().max()!=0:
            dists_position = dists_position/dists_position.max().max()
        print (pd.DataFrame(dists_position).head())

        dists_neigh = pairwise_distances(self.feature['distance_next_neigh'], metric='cosine')
        if dists_neigh.max().max()!=0:
            dists_neigh = dists_neigh/dists_neigh.max().max()
        print (pd.DataFrame(dists_neigh).head())

        dists_count_before = pairwise_distances(self.feature['distance_in_count_activity_before'], metric='manhattan')
        if dists_count_before.max().max()!=0:
            dists_count_before = dists_count_before/dists_count_before.max().max()
        print (pd.DataFrame(dists_count_before).head())

        dists_b_a = pairwise_distances(self.feature['distance_in_activity_seen_before'], metric='hamming')
        print (pd.DataFrame(dists_b_a).head())

        dists = pd.DataFrame((dists_b_a+dists_count_before+dists_position+dists_neigh)/4)

        self.distanceMatrix = dists

    def dm_aggregated(self, vector_aggregation, n_components=None):
        d = self.distanceMatrix.groupby(vector_aggregation).mean()
        if n_components:
            d = pd.DataFrame(TruncatedSVD(n_components=n_components).fit_transform(d), index=d.index)
        return d