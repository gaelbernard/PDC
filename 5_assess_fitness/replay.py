from Object.Log import Log
import pandas as pd
pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns',500)
pd.set_option('display.width',1000)

def conformance_complete(param):
    confidence_treshold = param[0]
    path_results = param[1]

    df = pd.read_csv(path_results)
    df.columns = ['case','confidence']
    print (df)
    df.set_index('case', inplace=True)
    df['fit'] = False
    return df['confidence']>=confidence_treshold

def conformance_imperative(path_results):
    df = pd.read_csv(path_results, skiprows=2, skipfooter=33, engine='python')
    df['Case IDs'] = df['Case IDs'].astype(str)

    results = {}
    for _, r in df.iterrows():
        results.update({case_id: r.to_dict() for case_id in r['Case IDs'].split('|')})

    df = pd.DataFrame(results).T
    df['case'] = df.index.astype(int)
    df.sort_values('case', inplace=True)
    df.set_index('case', inplace=True)
    df['conformance_imperative'] = df['Trace Fitness']==1
    for _, r in df.iterrows():
        if r['IsReliable'] != 'Yes':
            raise ValueError('The alignement is not reliable!')
    df = pd.DataFrame(df.loc[:,'conformance_imperative'])
    return df

def conformance_declarative(path_results):
    df = pd.read_csv(path_results)
    df.sort_values('traceName', inplace=True)
    df['conformance_declarative'] = df['alignmentFitness'] >= 1
    df = df[['conformance_declarative','traceName']]
    df.drop_duplicates(inplace=True)
    df.set_index('traceName', inplace=True)
    df.index.name = 'case'
    return df

def conformance_dmn(path_results, log, verbose=False):
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
        print ('{}% of the traces violate at least of the condition'.format(round(failed.shape[0]/dmn.shape[0]*100,2)))
        print ('traces that violates the constraint: {}'.format(failed.index))

    return pd.DataFrame(condition.all(axis=1), columns=['conformance_dmn'])


def replay(replay_setting):
    print (replay_setting)

    # Load logs
    log = Log()
    log.read_csv(replay_setting['path_log'])

    results_tests = []
    for name, path_results in replay_setting['tests'].items():
        if name == 'conformance_declarative':
            results_tests.append(conformance_declarative(path_results))
        elif name == 'conformance_dmn':
            results_tests.append(conformance_dmn(path_results, log))
        elif name == 'conformance_imperative':
            results_tests.append(conformance_imperative(path_results))
        elif name == 'conformance_complete':
            results_tests.append(conformance_complete(path_results))
        else:
            raise ValueError('Conformance test not know.')

    print (pd.concat(results_tests, axis=1))
    #print ('fit:', pd.concat(results_tests, axis=1).all(axis=1).sum())
    return pd.concat(results_tests, axis=1).all(axis=1)

root = '/Users/gbernar1/Desktop/pdc_3/PDC_repo'
replay_settings = {
    'feb-log1-training': {
        'path_log': '{}/data/csv/tests/feb-log1-training.csv'.format(root),
        'tests': {
            'conformance_declarative': '{}/results/log1/replay_declarative/feb.csv'.format(root),
            'conformance_dmn': '{}/results/log1/4_dmn/trees/rules.txt'.format(root),
            'conformance_complete': (0.5, '{}/results/log1/1_incomplete/output/score/proba_feb.csv'.format(root))
        },
        'comments': 'DONE 37/40'
    },
    'mar-log1-training': {
        'path_log': '{}/data/csv/tests/mar-log1-training.csv'.format(root),
        'tests': {
            'conformance_declarative': '{}/results/log1/replay_declarative/mar.csv'.format(root),
            'conformance_dmn': '{}/results/log1/4_dmn/trees/rules.txt'.format(root),
            'conformance_complete': (0.5, '{}/results/log1/1_incomplete/output/score/proba_feb.csv'.format(root))
        },
        'comments': 'DONE 37/37'
    },
    'feb-log2-training': {
        'path_log': '{}/data/csv/tests/feb-log2-training.csv'.format(root),
        'tests': {
            'conformance_imperative': '{}/results/log2/replay/feb.csv'.format(root),
            'conformance_complete': (0.5, '{}/results/log2/1_incomplete/output/score/proba_feb.csv'.format(root))
        },
        'comments': '40/40'
    },
    'mar-log2-training': {
        'path_log': '{}/data/csv/tests/mar-log2-training.csv'.format(root),
        'tests': {
            'conformance_imperative': '{}/results/log2/replay/mar.csv'.format(root),
            'conformance_complete': (0.5, '{}/results/log2/1_incomplete/output/score/proba_feb.csv'.format(root))
        },
        'comments': '39/40'
    },
    'feb-log3-training': {
        'path_log': '{}/data/csv/tests/feb-log3-training.csv'.format(root),
        'tests': {
            'conformance_imperative': '{}/results/log3/replay/feb.csv'.format(root),
            'conformance_complete': (0.5, '{}/results/log3/1_incomplete/output/score/proba_feb.csv'.format(root))
        },
        'comments': '39/40'
    },
    'mar-log3-training': {
        'path_log': '{}/data/csv/tests/mar-log3-training.csv'.format(root),
        'tests': {
            'conformance_imperative': '{}/results/log3/replay/mar.csv'.format(root),
            'conformance_complete': (0.5, '{}/results/log3/1_incomplete/output/score/proba_mar.csv'.format(root))
        },
        'comments': '38/40'
    },
    'feb-log4-training': {
        'path_log': '{}/data/csv/tests/feb-log4-training.csv'.format(root),
        'tests': {
            'conformance_imperative': '{}/results/log4/replay/feb.csv'.format(root),
            'conformance_complete': (0.5, '{}/results/log4/1_incomplete/output/score/proba_feb.csv'.format(root))
        },
        'comments': '34/38'
    },
    'mar-log4-training': {
        'path_log': '{}/data/csv/tests/mar-log4-training.csv'.format(root),
        'tests': {
            'conformance_imperative': '{}/results/log4/replay/mar.csv'.format(root),
            'conformance_complete': (0.5, '{}/results/log4/1_incomplete/output/score/proba_mar.csv'.format(root))

        },
        'comments': '38/40'
    },
    'feb-log5-training': {
        'path_log': '{}/data/csv/tests/feb-log5-training.csv'.format(root),
        'tests': {
            'conformance_imperative': '{}/results/log5/replay/feb.csv'.format(root),
            #'conformance_dmn': '{}/results/log5/4_dmn/trees/rules.txt'.format(root), # NONE FOUND
            'conformance_complete': (0.5, '{}/results/log5/1_incomplete/output/score/proba_feb.csv'.format(root))
        },
        'comments': '37/40'
    },
    'mar-log5-training': {
        'path_log': '{}/data/csv/tests/mar-log5-training.csv'.format(root),
        'tests': {
            'conformance_imperative': '{}/results/log5/replay/mar.csv'.format(root),
            #'conformance_dmn': '{}/results/log5/4_dmn/trees/rules.txt'.format(root), # NONE FOUND
            'conformance_complete': (0.5, '{}/results/log5/1_incomplete/output/score/proba_mar.csv'.format(root))
        },
        'comments': '36/40'
    },
    'feb-log6-training': {
        'path_log': '{}/data/csv/tests/feb-log6-training.csv'.format(root),
        'tests': {
            'conformance_imperative': '{}/results/log6/5_replay/feb.csv'.format(root),
            'conformance_complete': (0.2, '{}/results/log6/1_incomplete/output/score/proba_feb.csv'.format(root))
        },
        'comments': '36/40'
    },
    'mar-log6-training': {
        'path_log': '{}/data/csv/tests/mar-log6-training.csv'.format(root),
        'tests': {
            'conformance_imperative': '{}/results/log6/5_replay/mar.csv'.format(root),
            'conformance_complete': (0.2, '{}/results/log6/1_incomplete/output/score/proba_mar.csv'.format(root))
        },
        'comments': '38/40'
    },
    'feb-log7-training': {
        'path_log': '{}/data/csv/tests/feb-log7-training.csv'.format(root),
        'tests': {
            'conformance_declarative': '{}/results/log7/replay/feb.csv'.format(root),
            'conformance_complete': (.95, '{}/results/log7/1_incomplete/output/score/proba_feb.csv'.format(root))
        },
        'comments': ''
    },
    'mar-log7-training': {
        'path_log': '{}/data/csv/tests/mar-log7-training.csv'.format(root),
        'tests': {
            'conformance_declarative': '{}/results/log7/replay/mar.csv'.format(root),
            'conformance_complete': (.95, '{}/results/log7/1_incomplete/output/score/proba_mar.csv'.format(root))
        },
        'comments': ''
    },
    'feb-log8-training': {
        'path_log': '{}/data/csv/tests/feb-log8-training.csv'.format(root),
        'tests': {
            'conformance_declarative': '{}/results/log8/replay_declarative/feb.csv'.format(root),
            'conformance_complete': (.8, '{}/results/log8/1_incomplete/output/score/proba_feb.csv'.format(root))
        },
        'comments': '36/40'
    },
    'mar-log8-training': {
        'path_log': '{}/data/csv/tests/mar-log8-training.csv'.format(root),
        'tests': {
            'conformance_declarative': '{}/results/log8/replay_declarative/mar.csv'.format(root),
            'conformance_complete': (.8, '{}/results/log8/1_incomplete/output/score/proba_mar.csv'.format(root))
        },
        'comments': '36/40.'
    },
    'feb-log9-training': {
        'path_log': '{}/data/csv/tests/feb-log9-training.csv'.format(root),
        'tests': {
            'conformance_imperative': '{}/results/log9/replay/feb.csv'.format(root),
            'conformance_dmn': '{}/results/log9/4_dmn/trees/rules.txt'.format(root),
            'conformance_complete': (.6, '{}/results/log9/1_incomplete/output/score/proba_feb.csv'.format(root))
        },
        'comments': '36/40.'
    },
    'mar-log9-training': {
        'path_log': '{}/data/csv/tests/mar-log9-training.csv'.format(root),
        'tests': {
            'conformance_imperative': '{}/results/log9/replay/mar.csv'.format(root),
            'conformance_dmn': '{}/results/log9/4_dmn/trees/rules.txt'.format(root),
            'conformance_complete': (.6, '{}/results/log9/1_incomplete/output/score/proba_mar.csv'.format(root))
        },
        'comments': '32/40'
    },
    'feb-log10-training': {
        'path_log': '{}/data/csv/tests/feb-log10-training.csv'.format(root),
        'tests': {
            'conformance_imperative': '{}/results/log10/replay/feb.csv'.format(root),
            'conformance_dmn': '{}/results/log10/4_dmn/trees/rules.txt'.format(root),
            'conformance_complete': (.5, '{}/results/log10/1_incomplete/output/score/proba_feb.csv'.format(root))
        },
        'comments': '34/40'
    },
    'mar-log10-training': {
        'path_log': '{}/data/csv/tests/mar-log10-training.csv'.format(root),
        'tests': {
            'conformance_imperative': '{}/results/log10/replay/mar.csv'.format(root),
            'conformance_dmn': '{}/results/log10/4_dmn/trees/rules.txt'.format(root),
            'conformance_complete': (.5, '{}/results/log10/1_incomplete/output/score/proba_mar.csv'.format(root))
        },
        'comments': '31/40'
    },
}
output = pd.DataFrame({x:replay(replay_settings[x]) for x in ['mar-log10-training']})
#output = pd.DataFrame({x:replay(replay_settings[x]) for x in replay_settings.keys() if 'mar' in x})

print (output.apply(lambda x: x.astype(int).sum()))
print (output.apply(lambda x: x.astype(str).str.upper()))
