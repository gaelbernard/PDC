import pandas as pd
from collections import defaultdict
from sklearn.feature_extraction.text import CountVectorizer
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
from sklearn.metrics import pairwise_distances
from sklearn.decomposition import TruncatedSVD
import pandas as pd
from  Object.Log import Log
class Feature:
    '''
    We extract various features for all the activities observed in the event logs.
    Below we provide an example of the feature for the following log: [[a, b, c], [a, a]]

    We extract 4 types of features:
    1)  distance_position: distance matrix (manathan distance) of the relative position of the activity in the trace
               a  b  c  a  a
        a      0  1  2  0  1
        b      1  0  1  1  0
        c      2  1  0  2  1
        a      0  1  2  0  1
        a      1  0  1  1  0
    2)  distance_next_neigh: We look for the neighborhoods of each activities.
        we look (1) on the left, (2) on the right and (3) both left and right for several windows.
        We perform the three types of loop for windows of size 1 to 8
        For instance, below is a concatenation for left, window of 1, a right window of 2
        (left, window 1)   (right, window 2)
           a  b  c         a  b  c
        a  0  0  0         0  1  1
        b  1  0  0         0  0  1
        c  0  1  0         0  0  0
        a  0  0  0         1  0  0
        a  1  0  0         0  0  0
    3) distance_in_count_activity_before: distance matrix (manathan distance) counting
    the number of time the same activity label was seen before (on the left) in the same trace.
               a  b  c  a  a
        event
        a      0  0  0  0  1
        b      0  0  0  0  1
        c      0  0  0  0  1
        a      0  0  0  0  1
        a      1  1  1  1  0
    4) distance_in_activity_seen_before. For each letter of the alphabet,
       we check for each letter if the activity was seen before (label 3), if the activity was seen after (label 2)
       if the activity was seen before and after (label 1) or if it was not seen at all.
           a  b  c
        0  0  2  2
        1  1  0  2
        2  1  1  0
        3  2  0  0
        4  1  0  0  => We then measure the pairwise hamming distance


    Once all the distance has been measured, we average all the matrix to get average distance matrix:
           a         b         c         a         a
        a  0.000000  0.344225  0.578837  0.288475  0.719238
        b  0.344225  0.000000  0.344225  0.419238  0.438475
        c  0.578837  0.344225  0.000000  0.600000  0.591357
        a  0.288475  0.419238  0.600000  0.000000  0.529322
        a  0.719238  0.438475  0.591357  0.529322  0.000000

    ==> The closest activity to the first a happening in log a in the first a happening in the second trace.
    '''

    def __init__(self):
        self.feature = {
            'distance_position': None,
            'distance_next_neigh': None,
            'distance_in_count_activity_before': None,
            'distance_in_activity_seen_before': None,
        }
        self.distanceMatrix = None

    def distance_position(self, log):
        d = np.array([position for seq_aligned in log.seq for position, e in enumerate(seq_aligned) if e!='-']).reshape(-1, 1)
        d = pairwise_distances(d, metric='manhattan')
        self.feature['distance_position'] = d
        #print ('distance_position', pd.DataFrame(self.feature['distance_position'], index=log.vector_activities, columns=log.vector_activities).astype(int))


    def distance_in_count_activity_before(self, log):
        d = []
        for i in log.vector_activities.index:
            d.append(log.lefts[i].count(log.vector_activities[i]))

        self.feature['distance_in_count_activity_before'] =  pairwise_distances(np.array(d).reshape(-1, 1), metric='manhattan')
        #print ('distance_in_count_activity_before', pd.DataFrame(self.feature['distance_in_count_activity_before'], index=log.vector_activities, columns=log.vector_activities).astype(int))

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

        print ()
        f = pd.concat(f, axis=1)
        print ('distance_next_neigh')
        #print (f.loc[:,['a','b','c']])

        self.feature['distance_next_neigh'] =  f


    def distance_in_activity_seen_before(self, log):
        results = {}
        for i in log.vector_activities.index:
            results[i] = {}
            for l in log.alphabet:
                is_before = l in log.lefts[i]
                is_after = l in log.rights[i]
                if is_after and is_before:
                    v = 3
                elif is_after:
                    v = 2
                elif is_before:
                    v = 1
                else:
                    v = 0
                results[i][l] = v
        print ()
        print ('distance_in_activity_seen_before')
        print (pd.DataFrame(results).T)
        self.feature['distance_in_activity_seen_before'] = pairwise_distances(pd.DataFrame(results).T, metric='hamming')
        print (self.feature['distance_in_activity_seen_before'])


    def build_distanceMatrix(self, log):
        self.distance_position(log)
        self.distance_next_neigh(log)
        self.distance_in_count_activity_before(log)
        self.distance_in_activity_seen_before(log)
        self.get_distanceMatrix()

    def get_distanceMatrix(self):
        dists_position = self.feature['distance_position']
        if dists_position.max().max()!=0:
            dists_position = dists_position/dists_position.max().max()

        dists_neigh = pairwise_distances(self.feature['distance_next_neigh'], metric='cosine')
        if dists_neigh.max().max()!=0:
            dists_neigh = dists_neigh/dists_neigh.max().max()

        dists_count_before = self.feature['distance_in_count_activity_before']
        if dists_count_before.max().max()!=0:
            dists_count_before = dists_count_before/dists_count_before.max().max()

        dists_b_a = self.feature['distance_in_activity_seen_before']

        dists = pd.DataFrame((dists_b_a+dists_count_before+dists_position+dists_neigh)/4)

        self.distanceMatrix = dists
        #print (dists)

    def dm_aggregated(self, vector_aggregation, n_components=None):
        d = self.distanceMatrix.groupby(vector_aggregation).mean()
        if n_components:
            d = pd.DataFrame(TruncatedSVD(n_components=n_components).fit_transform(d), index=d.index)
        return d

# Load Logs
#log = Log()
#log.read_list([['a', 'b', 'c'], ['a', 'a']])

# Load
#f = Feature()
#f.build_distanceMatrix(log)
#feature = f.distanceMatrix
