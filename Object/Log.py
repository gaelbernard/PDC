import pandas as pd
from collections import defaultdict
class Log:
    """
    This class can be used to load a dataset as a CSV.
    From there, many usefull preprocessing are available
        - getting a list

    """
    def __init__(self):
        self.df = None                  # Raw CSV
        self.trace_col = None           # Column in CSV storing the trace ID
        self.activity_col = None        # Column in CSV storing the activity
        self.seq = None                 # The trace as a list e.g.,
                                        # e.g., [['c', 'h', 'j', 'f'], ['as', 'b', 'c', 'q',...
        self.max_seq_length = None      # Maximum length of a trace
        self.min_seq_length = None      # Minimum length of a trace
        self.vector_activities = None   # pd.Series() of all the event in order (i.e, self.df[self.activity_col] )
                                        # e.g., [['c', 'h', 'j', 'f', 'as', 'b', 'c', 'q',...
        self.vector_traces = None       # pd.Series() of all the trace_col in order (i.e, self.df[self.trace_col] )
                                        # e.g., [[0, 0, 0, 0, 1, 1, 1, 1,...
        self.alphabet = None            # Sorted list of the alphabet (== self.vector_activities.unique())
        self.left_padding = 'LEFT_padding'
        self.right_padding = 'RIGHT_padding'
        self.lefts = []                 # For all activities (i.e., self.vector_activities)
                                        # list all the activities that are on the left
                                        #   - belonging to the same trace
                                        #   - excl. the activity itself
                                        #   - add a special operator left_padding before (so that the list is never empty)
                                        # e.g., [['LEFT_padding'], ['LEFT_padding', 'c',], ['LEFT_padding', 'c', 'h'] ...
        self.rights = []                # Same as left...


    def __str__(self):
        return ('LOG    ==>   traces:{0}, events:{1}, activities:{2}'.format(len(self.seq), self.df.shape[0], len(self.activities_map)))

    def read_df (self, df, trace_col='case', activity_col='event', sep=','):
        self.df = df
        self._read(trace_col, activity_col)

    def read_csv(self, path, trace_col='case', activity_col='event', sep=','):
        # Loading CSV
        self.df = pd.read_csv(path, sep=sep)
        self._read(trace_col, activity_col)

    def read_list(self, log_list, trace_col='case', activity_col='event'):
        # Loading CSV
        activity = pd.Series([e for s in log_list for e in s], name=activity_col)
        trace = pd.Series([index for index, s in enumerate(log_list) for e in s], name=trace_col)
        self.df = pd.concat([activity, trace], axis=1)
        self._read(trace_col, activity_col)


    def _read(self, trace_col, activity_col):
        # Basic check
        if trace_col not in self.df.columns or activity_col not in self.df.columns:
            raise ValueError('One of the following columns: {0}, {1} is not in {2}'.format(trace_col, activity_col, self.df.columns))

        # Save columns information
        self.trace_col = trace_col
        self.activity_col = activity_col

        # Data is ready to be transformed
        self.prepare_data()



    def from_csv_to_list(self):
        # Make sure the activity name is in text (otherwise concatenation won't work)
        self.df.loc[:,self.activity_col] = self.df.loc[:,self.activity_col].astype(str)

        # For each traces, group by trace-id, concatenate activities; e.g., 1=>1-2-1, 2=>1-3-3-3-4-1 ... and transform to list
        return self.df.groupby(self.trace_col)[self.activity_col].apply(lambda x: x.values.tolist()).values.tolist()

    def prepare_data(self):
        self.seq = self.from_csv_to_list()


        # Find max and min lengths of trace
        self.max_seq_length = max([len(x) for x in self.seq])
        self.min_seq_length = min([len(x) for x in self.seq])
        self.count_seq = len(self.seq)

        # Some vectors that will be useful
        self.vector_activities = self.df[self.activity_col]
        self.vector_traces = self.df[self.trace_col]

        # Alphabet (unique activities observed in log)
        self.alphabet = list(sorted(self.vector_activities.unique().tolist()+[self.left_padding, self.right_padding]))

        # List all activities on the left
        for s in self.seq:
            for i, e in enumerate(s):
                self.lefts.append([self.left_padding]*1+s[:i])
                self.rights.append(s[i+1:]+[self.right_padding]*1)

    def list_to_csv(self, path, log=None):
        o = []
        if log is None:
            log = log.seq

        for case, s in enumerate(log):
            for event in s:
                o.append({'case':case, 'event':event})
        pd.DataFrame(o).to_csv(path, index=False)

    def to_xes(self, path):
        traces_ids = self.df[self.trace_col].unique().tolist()
        xes = '''<?xml version="1.0" encoding="UTF-8"?>
<log>
    <extension name="Concept" prefix="concept" uri="http://www.xes-standard.org/concept.xesext"/>
    <extension name="Lifecycle" prefix="lifecycle" uri="http://www.xes-standard.org/lifecycle.xesext"/>
'''
        for index, trace in enumerate(self.seq):
            xes+='	<trace>\n'
            xes+='      <string key="concept:name" value="{0}"/>\n'.format(traces_ids[index])
            for event in trace:
                xes+='      <event><string key="concept:name" value="{0}"/></event>\n'.format(event)
            xes+='	</trace>\n'
        xes+='</log>\n'

        if path is not None:
            with open(path, 'w') as myfile:
                myfile.write(xes)

        return xes
