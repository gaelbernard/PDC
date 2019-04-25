from Object.Log import Log
import pandas as pd

# Load DMN
log = Log()
log.read_csv('/Users/gbernar1/Desktop/pdc_3/PDC_repo/data/csv/tests/feb-log1-training.csv')
dmn = log.df
dmn.drop(['event'], axis=1, inplace=True)
dmn.drop_duplicates(inplace=True)
dmn.set_index('case', drop=True, inplace=True)

case = log.vector_traces.unique().tolist()
c = {}
for e in log.alphabet:
    c[e] = {}
    for i, s in enumerate(log.seq):
        c[e][case[i]] = e in s
happens = pd.DataFrame(c)

with open('/Users/gbernar1/Desktop/pdc_3/PDC_repo/4_dmn/trees/rules.txt', 'r') as f:
    condition = [eval(x) for x in f.read().splitlines()]

condition = pd.concat(condition, axis=1)
failed = condition[condition.all(axis=1) == False]
print ('{}% of the traces violate at least of the condition'.format(round(failed.shape[0]/dmn.shape[0]*100,2)))
print ('traces that violates the constraint: {}'.format(failed.index))
print (condition.all(axis=1))

