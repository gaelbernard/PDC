from Object.Log import Log
from constant import *
import numpy as np
from sklearn.metrics import silhouette_score
from sklearn.cluster import AgglomerativeClustering
import pandas as pd
from anytree.exporter import JsonExporter
from Object.Feature import Feature
from anytree import LevelOrderIter, Node, RenderTree
import matplotlib.pyplot as plt

def get_cluster(feature, k):
    label = AgglomerativeClustering(n_clusters=k).fit_predict(feature)
    return {id:feature.iloc[np.where(label==id)[0],:].index.values.tolist() for id in np.unique(label)}

def show_silhouette(feature):
    test_range = range(2,25)
    print ('####:')
    print ('silhouette:')
    o = {}
    for k in test_range:
        label = AgglomerativeClustering(n_clusters=k).fit_predict(feature)
        o[k] = silhouette_score(feature, label)
        print (k, o[k])
    o = pd.Series(o)
    o.to_csv('1_split/silhouette_score.csv', header=True)
    o.plot.line()
    plt.xticks(test_range)
    plt.grid()
    plt.savefig('silhouette_score.png')
    plt.close()


def filter_seq(seq, to_keep):
    s_n = []
    for s in seq:
        e_n = []
        for e in s:
            if e in to_keep:
                e_n.append(e)
        if len(e_n)!=0:
            s_n.append(e_n)
    return s_n

def get_abstract_log(seq, cluster):
    mapping = {e:str(c_id) for c_id, e_list in cluster.items() for e in list(e_list)}
    abstract_log = []
    for s in seq:
        abstract_e = []
        for e in s:
            if mapping[e] not in abstract_e:
                abstract_e.append(mapping[e])
        abstract_log.append(abstract_e)
    return abstract_log

# Load logs
log = Log()
log.read_csv('/Users/gbernar1/Desktop/pdc_3/PDC_repo/1_remove_uncomplete_trace_gael/output/dataset/dataset.csv')

c = {}
for e in log.alphabet:
    c[e] = {}
    for i, s in enumerate(log.seq):
        c[e][i] = s.count(e)
c = pd.DataFrame(c)

# Load feature
f = Feature()
f.build_distanceMatrix(log)
feature = f.dm_aggregated(log.vector_activities, n_components=100)

show_silhouette(feature)

# Build the tree
root = Node('root', discoveryAlgorithm="", nonReplayable="", log=log.seq)
cluster = get_cluster(feature, 7) #5
l = get_abstract_log(root.log, cluster)
for i, c in cluster.items():
    Node(str(i), discoveryAlgorithm="", nonReplayable="", log=filter_seq(root.log, c), parent=root)
root.log = l
print (RenderTree(root))

# Export the tree
exporter = JsonExporter(indent=2, sort_keys=True)
with open('1_split/rendertree.json', 'w') as f:
    exporter.write(root, f)

# Create the xes
for n in LevelOrderIter(root):
    l = Log()
    l.read_list(n.log)
    l.df.to_csv('1_split/{}.csv'.format(n.name))
    l.to_xes('1_split/{}.xes'.format(n.name))

