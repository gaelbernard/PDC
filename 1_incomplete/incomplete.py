import pandas as pd
from Object.Log import Log
from sklearn.tree import DecisionTreeClassifier
from Object.Feature import Feature
import matplotlib.pyplot as plt
import constant

# Update the dataset ID accordingly
dataset_id = 2

# We also leverage the training data to get more samples
files = {
    'feb': 'tests/feb-log{}-training.csv'.format(dataset_id),
    'mar': 'tests/mar-log{}-training.csv'.format(dataset_id),
    'overall': 'log{}-training.csv'.format(dataset_id),
}

# We create 1 big log that merges the data from training, feb and mar.
logs = {}
vector_names = []
for name, path in files.items():
    logs[name] = Log()
    logs[name].read_csv('{}/data/csv/{}'.format(constant.CURRENT_folder,path))
    vector_names.extend([name]*len(logs[name].seq))
vector_names = pd.Series(vector_names)
big_log = Log()
big_log.read_list([s for l in logs.values() for s in l.seq])

# LOAD FEATURE
f = Feature()
f.distance_next_neigh(big_log, onlyLeft=True)
feature = f.feature['distance_next_neigh']

# TRAIN CLASSIFIER AND PREDICT
is_it_uncomplete_trace = pd.Series([y!=1 for y in [len(x) for x in big_log.rights]]).astype(bool)
clf = DecisionTreeClassifier(random_state=0).fit(feature, is_it_uncomplete_trace)
global_proba = pd.DataFrame(clf.predict_proba(feature[is_it_uncomplete_trace!=True]), index=big_log.vector_traces.unique())[0]
global_proba.index.name = 'case_id'

################
# Loop through
for type in files.keys():

    sub_proba = global_proba[vector_names==type]
    sub_proba.index = logs[type].df['case'].unique()

    p_display = sub_proba.sort_values().copy().reset_index(drop=True)

    # BUILD GRAPH
    to_plt = p_display.round(5)
    to_plt.plot()
    plt.ylabel('Confidence to be complete')
    plt.xlabel('Number of activities to cut')
    if type == 'overall':
        plt.vlines(140,0,1, linestyles='dashed')
    plt.savefig('output/plt/{}.png'.format(type))
    if type == 'overall':
        plt.show()
    plt.close()

    sub_proba.to_csv('output/score/proba_{}.csv'.format(type), index=True, header=True)

    # PREVIEW
    s = sub_proba.round(2).tolist()
    for pos, trace_index in enumerate(logs[type].vector_traces.unique()):
        print ('{}\t{}\t{}\t{}'.format(type, trace_index, s[pos], logs[type].seq[pos]))

    # Cut the training log
    if type == 'overall':
        print (p_display.to_dict())
        how_many_to_cut = int(input('how many activities to cut?:'))

        # CUT according to treshold
        sub_proba = sub_proba.nlargest(len(logs['overall'].seq)-how_many_to_cut)

        # EXPORT cut CSV
        d = pd.read_csv('{}/data/csv/{}'.format(constant.CURRENT_folder,files['overall']))
        d = d[d['case'].isin(sub_proba.index)]
        d.to_csv('output/dataset/dataset.csv', index=False)

