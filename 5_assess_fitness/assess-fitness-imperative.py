import pandas as pd
pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns',500)
pd.set_option('display.width',1000)
from Object.Log import Log
k = 1
dataset = 'log{}'.format(k)
for name in ['mar']: # 'overall', 'feb', 'mar'

    df = pd.read_csv('/Users/gbernar1/Desktop/pdc_3/PDC_repo/results/{}/replay/{}.csv'.format(dataset, name), skiprows=2, skipfooter=33, engine='python')
    df['Case IDs'] = df['Case IDs'].astype(str)

    results = {}
    for _, r in df.iterrows():
        results.update({case_id: r.to_dict() for case_id in r['Case IDs'].split('|')})

    df = pd.DataFrame(results).T
    df['Case IDs'] = df.index.astype(int)
    df.sort_values('Case IDs', inplace=True)
    print ('REPORT: {}'.format(name))
    print ('Fitting: {} on {}'.format(df[df['Trace Fitness']==1].shape[0], df.shape[0])) # Move-Model Fitness
    for _, r in df.iterrows():
        if r['IsReliable'] != 'Yes':
            raise ValueError('The alignement is not reliable!')
        print (r['Case IDs'], str(r['Trace Fitness']==1).upper())
