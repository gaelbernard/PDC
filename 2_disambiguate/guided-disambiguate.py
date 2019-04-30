from Object.Log import Log
import pandas as pd
from sklearn.cluster import DBSCAN, KMeans, AgglomerativeClustering, SpectralClustering
from Object.Feature import Feature
pd.options.mode.chained_assignment = None  # default='warn'
import numpy as np
from flask import Flask
app = Flask(__name__)
from flask_cors import CORS
import urllib.parse
import json
import constant
def get_worst(feature, vector, rejected):
    '''
    The worst activity is the one having the biggest distance
    '''
    min_score = {}
    for l in np.unique(vector):
        if l in rejected:
            continue
        if l in [log.left_padding, log.right_padding]:
            continue
        index_activity = vector[vector == l].index.values

        if len(index_activity)<=2:
            continue
        subset = feature.iloc[index_activity,index_activity]
        min_score[l] = subset.max().max()

    worst = pd.Series(min_score).idxmax()
    print ('worst:', worst, min_score[worst])
    return worst

def disambiguate(l, feature, vector):
    '''
    We disambiguate by clustering the activities using an agglomerative clustering
    '''
    index_activity = vector[vector == l].index.values
    subset = feature.iloc[index_activity,index_activity]
    for k in range(2, 3):
        if subset.shape[0] <= k:
            continue
        label = pd.Series(AgglomerativeClustering(n_clusters=k, affinity='precomputed', linkage='complete').fit_predict(subset)).astype(str).values
        v = vector.copy()
        v[index_activity] = v[index_activity]+'$'+label
    return v

def show_seq(vector):
    '''
    Transform a sequence of activities in a list of activities
    '''
    new_seq = []
    i=0
    for s in log.seq:
        new_t = []
        for e in s:
            new_t.append(vector[i])
            i+=1
        new_seq.append(new_t)
    return new_seq

def goToNext():
    '''
    Get the next letter, will until we reach the last "worst" activities (the one having the smallest distance)
    '''
    worst_letter = get_worst(feature, new_vector, rejected)
    potential_new_vector = disambiguate(worst_letter, feature, new_vector)
    v = potential_new_vector[new_vector==worst_letter]
    g = [[int(l) for l in v[v==v_u].index.values] for v_u in v.unique()]
    data = {'activity':worst_letter, 'index':g, 'seq':show_seq(potential_new_vector), 'alphabet':list(set(potential_new_vector.values)), 'activity_u':list(set(v.values))}
    return worst_letter, potential_new_vector, data

# Load Logs
log = Log()
log.read_csv('{}/1_incomplete/output/dataset/dataset.csv').format(constant.CURRENT_folder)

# Load features
f = Feature()
f.build_distanceMatrix(log)
feature = f.distanceMatrix

# Start the process
new_vector = log.vector_activities
rejected = []
worst_letter, potential_new_vector, data = goToNext()

# Prepare API
CORS(app)
@app.route('/getCurrent')
def getCurrent():
    return json.dumps(data)

@app.route('/reject')
def reject():
    global worst_letter, new_vector, data
    rejected.append(worst_letter)
    worst_letter, potential_new_vector, data = goToNext()
    return json.dumps("1")

@app.route('/accept/<path:labels>')
def accept(labels):
    global worst_letter, new_vector, data
    labels = json.loads(urllib.parse.unquote(labels))
    new_vector = pd.Series(labels)
    worst_letter, potential_new_vector, data = goToNext()
    return json.dumps("1")

@app.route('/save')
def save():
    global worst_letter, new_vector, data
    log.df['event'] = new_vector
    d = log.df.loc[:,['case','event']]
    d.to_csv('output/dataset.csv', index=False)
    return json.dumps("1")

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=81)
