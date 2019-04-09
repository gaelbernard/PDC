import pandas as pd
from Object.Log import Log

for dataset_id in range(1,11):
    name = "mar-log{}-training".format(dataset_id)

    # Loading Logs
    log = Log()
    log.read_csv("/Users/gbernar1/Desktop/pdc_3/PDC_repo/data/csv/tests/{}.csv".format(name), "case", "event")

    # Make Xes File
    log.to_xes("/Users/gbernar1/Desktop/pdc_3/PDC_repo/data/xes/tests/{}.xes".format(name))
