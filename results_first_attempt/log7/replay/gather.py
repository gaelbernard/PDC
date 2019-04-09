import pandas as pd

d = {}
for p in ['0','1']:
    df = pd.read_csv('{}_mar.csv'.format(p))
    df.drop_duplicates('traceName', inplace=True)
    df = df.set_index('traceName', drop=True)['alignmentFitness']
    df.sort_index(inplace=True)
    d[p] = df
d = pd.concat(d, axis=1)
d.max()
for fit in (d.min(axis=1)==1).tolist():
    print (str(fit).upper())