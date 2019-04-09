import os
from pm4py.objects.log.importer.xes import factory as xes_importer
from pm4py.algo.discovery.inductive import factory as inductive_miner

log = xes_importer.import_log("/Users/gbernar1/Desktop/pdc_3/PDC_repo/data/xes/tests/feb-log7-training.xes")

from pm4py.objects.petri.importer import pnml as pnml_importer

net, initial_marking, final_marking = pnml_importer.import_net("/Users/gbernar1/Desktop/pdc_3/PDC_repo/results/log7/3_cIM/2_gather/petri.pnml")

from pm4py.algo.conformance.alignments import factory as align_factory

alignments = align_factory.apply_log(log, net, initial_marking, final_marking)
print (alignments)  