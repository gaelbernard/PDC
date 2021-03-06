import pandas as pd
from Object.Log import Log
import constant

def conformance_dmn(path_results, log, verbose=True):
    global dmn, happens
    dmn = log.df.copy()
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

    with open(path_results, 'r') as f:
        condition = []
        for x in f.read().splitlines():
            try:
                condition.append(eval(x))
            except KeyError as k:
                print ('key error: ',k)
            except:
                raise ValueError('error')

    condition = pd.concat(condition, axis=1)
    failed = condition[condition.all(axis=1) == False]
    if verbose:
        print (condition)
        print (condition.all(axis=1))
        print ('{}% of the traces violate at least of the condition'.format(round(failed.shape[0]/dmn.shape[0]*100,2)))
        print ('traces that violates the constraint: {}'.format(failed.index))
    condition.to_excel('report.xls')
    return pd.DataFrame(condition.all(axis=1), columns=['conformance_dmn'])

path_dataset = '{}/0_data/csv/log10-training.csv'.format(constant.CURRENT_folder)
path_rules = '{}/results/log10/4_dmn/trees/rules.txt'.format(constant.CURRENT_folder)
log = Log()
log.read_csv(path_dataset)
conformance_dmn(path_rules, log)
