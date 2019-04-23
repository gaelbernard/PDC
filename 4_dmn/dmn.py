# Load logs
from Object.Log import Log
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score
from sklearn.tree import export_graphviz
log = Log()
log.read_csv('/Users/gbernar1/Desktop/pdc_3/PDC_repo/data/csv/log1-training.csv')

dmn = log.df.copy()
dmn.drop(['event'], axis=1, inplace=True)
dmn.drop_duplicates(inplace=True)
dmn.set_index('case', drop=True, inplace=True)
case = log.vector_traces.unique().tolist()
c = {}
for e in log.alphabet:
    c[e] = {}
    for i, s in enumerate(log.seq):

        c[e][case[i]] = s.count(e)
c = pd.DataFrame(c)

dmn = pd.concat([dmn, c], axis=1)
train, test = train_test_split(dmn, test_size=0.2)

for l in log.alphabet:
    if l in ['LEFT_padding', 'RIGHT_padding']:
        continue
    train_altered = train.drop([l], axis=1)
    test_altered = test.drop([l], axis=1)
    y_train = c.loc[train_altered.index,l]
    y_test = c.loc[test_altered.index,l]


    tree = DecisionTreeClassifier()
    tree.fit(train_altered, y_train)
    prediction = tree.predict(test_altered)
    print ()
    print (l, f1_score(prediction, y_test, average='micro'))
    print (list(reversed(sorted(zip(tree.feature_importances_.round(2), train_altered.columns)))))
    print (prediction)
    best_feature = train_altered.columns[tree.feature_importances_.argmax()]
    export_graphviz(tree, out_file='trees/{}.dot'.format(l), feature_names=train_altered.columns)

    #model = SelectFromModel(tree, prefit=True)
    #new_dmn = model.transform(dmn)
    x = dmn[best_feature].values.reshape(-1, 1)

    tree2 = DecisionTreeClassifier(max_depth=1)
    tree2.fit(x, c.loc[:,l])
    prediction = tree2.predict(x)
    print (l, f1_score(prediction, c.loc[:,l], average='micro'))
    export_graphviz(tree2, out_file='trees/{}2.dot'.format(l), feature_names=[best_feature])



