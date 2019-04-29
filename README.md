#Process Discovery Challenge

## Introduction
This is our contribution for the [Process Discovery Challenge](https://icpmconference.org/process-discovery-contest). More information about our approach are available [here](TODO).

## How to use
Our algorithm is composed of 4 steps that you should apply sequentially.
1. Remove incomplete trace
2. Disambiguate activity (recurrent activities)
3. Cut the traces before applying the Inductive Miner
4. Mine DMN rules

###Step 1: remove the trace that are considered incomplete
We know for a fact that 20% of the traces are incomplete. We remove them using the script: *[1_incomplete/incomplete.py](1_incomplete/incomplete.py)*. 
 
 1. Update the dataset ID 
```python
dataset_id = 10
```
 2. Run 1_incomplete/incomplete.py. Use the generated charts (1_incomplete/plt/) to select the number of traces to cut. Below we can cleary see a lift at 140. Hence, 140 would be a good choice. Enter 140 and press enter.
```python
how many activities to cut?:140
```
![ds](results/log4/1_incomplete/output/plt/overall.png)

3. The output, the dataset without the incomplete trace, is available in 1_incomplete/dataset/dataset.csv

###Step 2: rename the activities that are ambiguous
###Step 3: find cuts in the traces before feeding it to the inductive miner
###Step 4: Mine rules
