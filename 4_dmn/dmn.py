# Load logs
from Object.Log import Log
import pandas as pd
from sklearn.tree import DecisionTreeClassifier, ExtraTreeClassifier, DecisionTreeRegressor
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score, adjusted_mutual_info_score
from sklearn.tree import export_graphviz
from sklearn.feature_selection import SelectFromModel
log = Log()
log.read_csv('/Users/gbernar1/Desktop/pdc_3/PDC_repo/results/log5/1_remove_uncomplete_trace_gael/output/dataset/dataset.csv')

'''
The goal is discover the strong correlation between the execution of an activity AND a rule in the DMN table
'''

# FEATURE: DMN data table
'''     z_2       z_1    z_4    z_3       z_6       z_5    z_8    z_7       z_9
case
0      True  0.980450   True   True  0.031824  0.720246   True  False  0.441958
1     False  0.123825   True   True  0.842157  0.479376   True   True  0.681340
2      True  0.788096   True   True  0.066936  0.390624  False   True  0.667809
'''
dmn = log.df
dmn.drop(['event'], axis=1, inplace=True)
dmn.drop_duplicates(inplace=True)
dmn.set_index('case', drop=True, inplace=True)
case = log.vector_traces.unique().tolist()

# TARGET: Count the number of activities
'''
    a  aa  ab  ac  ad  ae  ...  s  t  u  v  w  x  y  z
0   0   0   1   0   0   0  ...  0  1  0  0  1  0  0  0
1   1   0   0   0   0   1  ...  1  2  0  0  0  0  1  1
2   0   0   0   0   0   0  ...  1  1  0  0  0  0  0  1
'''
c = {}
for e in log.alphabet:
    c[e] = {}
    for i, s in enumerate(log.seq):
        c[e][case[i]] = e in s
c = pd.DataFrame(c)

for l in log.alphabet:
    if l in ['LEFT_padding', 'RIGHT_padding']:
        continue
    if c.loc[:,l].var() <= 0.01:
        continue

    # Split 20% test - 80% training
    train, test = train_test_split(dmn, test_size=0.1, stratify=c.loc[:,l])

    # What we try to predict is the count of the activity l (i.e., target)
    y_train = c.loc[train.index,l]
    y_test = c.loc[test.index,l]

    tree = DecisionTreeClassifier(max_leaf_nodes=3)
    tree.fit(train, y_train)
    prediction = tree.predict(test)

    f1 = f1_score(prediction, y_test, average='micro')
    mutual_info = round(adjusted_mutual_info_score(prediction, y_test, average_method='arithmetic'),3)
    tree_score = tree.score(train, y_train)
    if f1 > 0.96 and mutual_info > 0.2 and tree_score > 0.96:
        print ()
        print (l)
        print ('tree1:::::')
        print ('tree score:', tree_score)
        print ('f1_score:', f1)
        print ('adjusted_mutual_info_score:', mutual_info)
        print (list(reversed(sorted(zip(tree.feature_importances_.round(2), train.columns)))))
        print (prediction)
        print (y_test.values)
        best_feature = train.columns[tree.feature_importances_.argmax()]
        export_graphviz(tree, out_file='trees/{}.dot'.format(l), feature_names=train.columns)

