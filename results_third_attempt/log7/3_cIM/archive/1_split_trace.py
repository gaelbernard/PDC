from Object.Log import Log
from constant import *
import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.cluster import AgglomerativeClustering
import pandas as pd
from anytree.exporter import JsonExporter
from Object.Feature import Feature
from anytree import LevelOrderIter, Node, RenderTree

def get_cluster(feature, k):
    label = AgglomerativeClustering(n_clusters=k).fit_predict(feature)
    return {id:feature.iloc[np.where(label==id)[0],:].index.values.tolist() for id in np.unique(label)}

def show_silhouette(feature):
    print ('####:')
    print ('silhouette:')
    o = {}
    for k in range(2,16):
        label = AgglomerativeClustering(n_clusters=k,  affinity='cosine', linkage='complete').fit_predict(feature)
        o[k] = silhouette_score(feature, label)
        print (k, o[k])
    pd.Series(o).to_csv('1_split/silhouette_score.csv', header=True)

# Load logs
log = Log()
log.read_csv('/Users/gbernar1/Desktop/pdc_3/PDC_repo/1_remove_uncomplete_trace_gael/output/dataset/dataset.csv')


c = {}
for e in log.alphabet:
    c[e] = {}
    for i, s in enumerate(log.seq):
        c[e][i] = s.count(e)
c = pd.DataFrame(c)

c.index = log.vector_traces.unique()
feature = c


def get_abstract_log(seq, cluster):
    mapping = {e:str(c_id) for c_id, e_list in cluster.items() for e in list(e_list)}
    sort_keys = sorted(mapping.keys())
    return [mapping[i] for i in sort_keys]

# Load feature
#f = Feature()
#f.build_distanceMatrix(log)
#feature = f.dm_aggregated(log.vector_traces, n_components=100)

show_silhouette(feature)

# Build the tree
root = Node('root', discoveryAlgorithm="", nonReplayable="", log=log.seq)
cluster = get_cluster(feature, 2)

print (cluster)

l = get_abstract_log(root.log, cluster)

v = log.vector_traces.unique().tolist()
for i, c in cluster.items():
    Node(str(i), discoveryAlgorithm="", nonReplayable="", log=[log.seq[v.index(i)] for i in c], parent=root)

root.log = l
print (RenderTree(root))

# Export the tree
exporter = JsonExporter(indent=2, sort_keys=True)
with open('1_split_traces/rendertree.json', 'w') as f:
    exporter.write(root, f)

# Create the xes
for n in LevelOrderIter(root):
    if l:
        l = Log()
        l.read_list(n.log)
        l.df.to_csv('1_split_traces/{}.csv'.format(n.name))
        l.to_xes('1_split_traces/{}.xes'.format(n.name))
