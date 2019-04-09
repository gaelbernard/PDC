from Object.Log import Log
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import TruncatedSVD
import pandas as pd
from Object.Feature import Feature
from sklearn.tree import DecisionTreeClassifier
from sklearn.feature_selection import SelectFromModel
import random

month = 'feb'

dataset_original = '/Users/gbernar1/Desktop/pdc_3/PDC_repo/results/log7/1_remove_uncomplete_trace_gael/output/dataset/dataset.csv'
test = '/Users/gbernar1/Desktop/pdc_3/PDC_repo/data/csv/tests/mar-log7-training.csv'

logs = []
type_vector = []

log = Log()
log.read_csv(dataset_original, activity_col='event', trace_col='case')
logs.extend(log.seq)
type_vector.extend(['original']*len(log.seq))

log = Log()
log.read_csv(test, activity_col='event', trace_col='case')
logs.extend(log.seq)
type_vector.extend(['test']*len(log.seq))

for k in range(1):
    fake = []
    for s in log.seq:
        remove_index = random.randint(0, len(s)-1)
        place_index = remove_index
        while place_index == remove_index:
            place_index = random.randint(0, len(s)-1)
        a = s.pop(remove_index)
        s.insert(place_index, a)
        fake.append(s)


    logs.extend(fake)
    type_vector.extend(['fake']*len(log.seq))


c = {}
for e in log.alphabet:
    c[e] = {}
    for i, s in enumerate(logs):
        c[e][i] = s.count(e)
c = pd.DataFrame(c)
f = c

type_vector = pd.Series(type_vector)



#cv = CountVectorizer(ngram_range=(2,2), token_pattern='[^$]+', binary=False)
#data = cv.fit_transform(['$'.join(s) for s in logs])
#f = pd.DataFrame(data.toarray(), columns=cv.get_feature_names())

training_feature = f.loc[type_vector!='test',:]
test_feature = f.loc[type_vector=='test',:]

dtc = DecisionTreeClassifier()
dtc.fit(training_feature, type_vector[type_vector!='test'])

model = SelectFromModel(dtc, prefit=True, max_features=100)
sub_f = pd.DataFrame(model.transform(f))

sdtc = DecisionTreeClassifier()
sdtc.fit(sub_f.loc[type_vector!='test',:], type_vector[type_vector!='test'])
r = pd.DataFrame(sdtc.predict_proba(sub_f.loc[type_vector=='test',:]), columns=['original','test'])
print ('original:', r[r['original']>0.5].shape[0])







'''
journey_ngrams_2D = pd.DataFrame(TruncatedSVD(n_components=2).fit_transform(f))
for i, t in enumerate(type_vector.unique()):
    index = type_vector[type_vector==t].index
    plt.scatter(journey_ngrams_2D.loc[index, 0], journey_ngrams_2D.loc[index, 1], marker="x", c=scalarMap.to_rgba(i))

plt.show()
'''
