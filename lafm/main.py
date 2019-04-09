from Object.Log import Log
import pandas as pd
from anytree import Node, LevelOrderIter, RenderTree
from lafm.object.Tree import Tree
from lafm.object.Replayer import Replayer
from lafm.object.PetriNetBuilder import PetriNetBuilder

pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

original_log = "/Users/gbernar1/Desktop/pdc_3/PDC_repo/results/log4/2_disambiguate_activities/output/dataset.csv"
#replay_results = "/Users/gbernar1/Desktop/pdc_3/PDC_repo/results/log9-training/05-testReplay/1.csv"

log = Log()
log.read_csv(original_log)

t = Tree()
t.read_ptml('/Users/gbernar1/Desktop/pdc_3/PDC_repo/results/log1/3_cIM/2_gather/pt.ptml')

pn = PetriNetBuilder(t.root)

r = Replayer(pn, t.root, log.seq)

r.build_matrix()

print (r.abstract_df)
print (r.df)
exit()



df = pd.read_csv(replay_results)
print (df['EVTAL:TransitionID'])