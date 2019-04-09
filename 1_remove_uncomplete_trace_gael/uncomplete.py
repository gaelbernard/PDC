import pandas as pd
from Object.Log import Log
from sklearn.tree import DecisionTreeClassifier
from Object.Feature import Feature
from constant import *
import matplotlib.pyplot as plt

dataset_id = 2
dataset = 'log{}-training.csv'.format(dataset_id)
csv_path = '{}/data/csv/{}'.format(CURRENT_folder, dataset)

# LOAD LOGS
log = Log()
log.read_csv(csv_path)

# LOAD FEATURE
f = Feature()
f.distance_next_neigh(log, onlyLeft=True)
feature = f.feature['distance_next_neigh']


# TRAIN CLASSIFIER AND PREDICT
is_it_uncomplete_trace = pd.Series([y!=1 for y in [len(x) for x in log.rights]]).astype(bool)
clf = DecisionTreeClassifier(random_state=0).fit(feature, is_it_uncomplete_trace)
p = pd.DataFrame(clf.predict_proba(feature[is_it_uncomplete_trace!=True]), index=log.vector_traces.unique())[0]

# p_display discard the real index to sort by score
p_display = p.sort_values().reset_index(drop=True).copy()
p_display.index = p_display.index+1

# BUILD GRAPH
to_plt = p_display.round(4)[0:700].round(3)
to_plt.plot()
plt.ylabel('Confidence to be complete')
plt.xlabel('Number of activities to cut')
plt.vlines(140,0,1, linestyles='dashed')
plt.title('Remove uncomplete activities: ')
plt.savefig('output/plt/plot.png')
plt.close()

# INTERACTING with user
print (p_display.to_dict())
how_many_to_cut = int(input('how many activities to cut?:'))

# CUT according to treshold
complete = p.nlargest(len(log.seq)-how_many_to_cut)
complete.to_csv('output/score/score.csv', index=False, header=True)

# EXPORT cut CSV
d = pd.read_csv(csv_path)
d = d[d['case'].isin(complete.index)]
d.to_csv('output/dataset/dataset.csv', index=False)

# PREVIEW
traces_index = log.vector_traces.unique()
for pos, trace_index in enumerate(traces_index):
    status = 'UNcomplete'
    if trace_index in complete.index:
        status = '__complete'
    print ('{} \t {} \t {}'.format(trace_index, status, log.seq[pos]))



