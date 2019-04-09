import pandas as pd
pd.set_option('display.max_rows',500)
pd.set_option('display.max_columns',500)
pd.set_option('display.width',1000)
from Object.Log import Log
for k in range(1,11):
    dataset = 'log{}'.format(k)
    for name in ['mar']: # 'overall', 'feb', 'mar'

        if k==7:
            continue

        log = Log()
        log.read_csv('/Users/gbernar1/Desktop/pdc_3/PDC_repo/data/csv/tests/{}-{}-training.csv'.format(name, dataset))

        #for name in ['result-report-original']:
        df = pd.read_csv('/Users/gbernar1/Desktop/pdc_3/PDC_repo/results/{}/replay/{}.csv'.format(dataset, name), skiprows=2, skipfooter=33, engine='python')
        df['Case IDs'] = df['Case IDs'].astype(str)

        results = {}
        for _, r in df.iterrows():
            results.update({case_id: r.to_dict() for case_id in r['Case IDs'].split('|')})

        df = pd.DataFrame(results).T
        df['Case IDs'] = df.index.astype(int)
        df.sort_values('Case IDs', inplace=True)
        print (df.columns)
        print ('')
        print ('############')
        print ('REPORT: {}'.format(name))
        print ('Fitting: {} on {}'.format(df[df['Move-Model Fitness']==1].shape[0], df.shape[0]))
        for _, r in df.iterrows():
            continue
            #if r['IsReliable'] != 'Yes':
            #    raise ValueError('The alignement is not reliable!')
            print (str(r['Move-Model Fitness']==1).upper())

        print ('########')
        print ('Classified as fitting:')
        for _, r in df[df['Move-Model Fitness']==1].iterrows():

            print (_, log.seq[int(_)])
        print ()
        print ('Classified as NOT fitting:')
        for _, r in df[df['Move-Model Fitness']<1].iterrows():
            continue
            print (_, log.seq[int(_)])

        del df