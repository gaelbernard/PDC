from Object.Log import Log
import pandas as pd
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import f1_score, accuracy_score, adjusted_mutual_info_score
from sklearn.tree import export_graphviz
log = Log()
log.read_csv('/Users/gbernar1/Desktop/pdc_3/PDC_repo/results/log10/2_disambiguate_activities/output/dataset.csv')

'''
The goal is discover the strong correlation between the execution of an activity AND a rule in the DMN table
'''


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
    activities_to_test = set(log.alphabet)
    activities_to_test.remove(l)
    activities_to_test.remove('LEFT_padding')
    activities_to_test.remove('RIGHT_padding')
    linked = []
    while len(activities_to_test) > 0:
        local_c = c.loc[:,activities_to_test]

        # Split 20% test - 80% training
        train, test = train_test_split(local_c, test_size=0.001, stratify=c.loc[:,l])

        # What we try to predict is the count of the activity l (i.e., target)
        y_train = c.loc[train.index,l]
        y_test = c.loc[test.index,l]

        tree = DecisionTreeClassifier(max_leaf_nodes=2)
        tree.fit(train, y_train)
        prediction = tree.predict(test)

        f1 = f1_score(prediction, y_test, average='micro')
        mutual_info = round(adjusted_mutual_info_score(prediction, y_test, average_method='arithmetic'),3)
        tree_score = tree.score(train, y_train)
        best_feature = train.columns[tree.feature_importances_.argmax()]
        score, letter = list(reversed(sorted(zip(tree.feature_importances_.round(2), train.columns))))[0]
        if f1 > 0.97 and mutual_info > 0.5 and tree_score > 0.97 and score > 0.97:
            linked.append(letter)
            activities_to_test.remove(letter)
            export_graphviz(tree, out_file='trees/ltd_{}_{}.dot'.format(l,letter), feature_names=train.columns)

            continue
            print ()
            print (l)
            print ('tree1:::::')
            print ('tree score:', tree_score)
            print ('f1_score:', f1)
            print ('adjusted_mutual_info_score:', mutual_info)
            print (list(reversed(sorted(zip(tree.feature_importances_.round(2), train.columns)))))
            print (prediction)
            print (y_test.values)

        else:
            break
    print (l, linked)

