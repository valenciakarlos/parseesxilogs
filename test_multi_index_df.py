# Executes ssh to a host and provides aggregate and per lcore stats 
import paramiko
import time
import difflib
import os
import json
import re
import json
import pandas as pd
import argparse
from prettytable import PrettyTable
import time
import math


def validate_arguments():
    parser = argparse.ArgumentParser(description="SSH to a host and collects per lcore and aggregate flow stats")
    # The first argument, input_file, is a positional argument (required).
    parser.add_argument("hostname", help="Hostname to check")
    parser.add_argument("-i", "--iterations", type=int, help="Number if Iterations", default=6)
    parser.add_argument("-d", "--duration", type=int, help="Duration of each iteration", default=5)

    args = parser.parse_args()
    return args

def calculate_ratios(lcore_idx, lcore_df):
    # Receives a dataframe with counter for an lcore and returns a dictionary with the ratios
    dict_ratios={}

    hits = lcore_df.loc[lcore_idx,'hits']
    miss = lcore_df.loc[lcore_idx,'miss']
    slowpath = lcore_df.loc[lcore_idx,'slowpath']
    localHits = lcore_df.loc[lcore_idx,'localHits']

    total_events = hits + miss + slowpath + localHits
    # dict_ratios['total_events']=total_events
    slowpath_ratio = slowpath / total_events
    dict_ratios['slowpath_ratio'] = slowpath_ratio
    hits_ratio = (hits + localHits) / total_events
    dict_ratios['hits_ratio'] = hits_ratio
    miss_ratio = miss / total_events
    dict_ratios['miss_ratio'] = miss_ratio
    hits_to_miss_ratio = (hits + localHits) / (hits + localHits + miss)
    dict_ratios['hits_to_miss_ratio'] = hits_to_miss_ratio
    miss_to_hits_ratio = miss / (hits + localHits + miss)
    dict_ratios['miss_to_hits_ratio'] = miss_to_hits_ratio
    print(f"Lcore={lcore_idx} Hits Ratio={hits_ratio:.2%} Slowpath ratio={slowpath_ratio:.2%} Miss ratio={miss_ratio:.2%} Hits to Miss ratio={hits_to_miss_ratio:.2%} Miss to Hits ratio={miss_to_hits_ratio:.2%} ")

    return dict_ratios

'''
def calculate_ratios_vectorized(row):
    total_events = row['hits'] + row['miss'] + row['slowpath'] + row['localHits']
    return {
        'slowpath_ratio': row['slowpath'] / total_events,
        'hits_ratio': (row['hits'] + row['localHits']) / total_events,
        'miss_ratio': row['miss'] / total_events,
        'hits_to_miss_ratio': (row['hits'] + row['localHits']) / (row['hits'] + row['localHits'] + row['miss']),
        'miss_to_hits_ratio': row['miss'] / (row['hits'] + row['localHits'] + row['miss'])
    }

'''

def calculate_ratios_vectorized(row):
    total_events = row['hits'] + row['miss'] + row['slowpath'] + row['localHits']
    return pd.Series({
        'slowpath_ratio': row['slowpath'] / total_events,
        'hits_ratio': (row['hits'] + row['localHits']) / total_events,
        'miss_ratio': row['miss'] / total_events,
        'hits_to_miss_ratio': (row['hits'] + row['localHits']) / (row['hits'] + row['localHits'] + row['miss']),
        'miss_to_hits_ratio': row['miss'] / (row['hits'] + row['localHits'] + row['miss'])
    })



# Does some calculations if the DF has all the info we need
# Receives two data frames and provides the ratio of slow path to misses
def get_ratios(df_one,df_two):
    # Returns a dictionary with all the ratios calculated
    dict_ratios={}
    try:
        # Try to extract the value for the indexes we need
        hits=df_two.loc['hits',0]-df_one.loc['hits',0]
        miss=df_two.loc['miss',0]-df_one.loc['miss',0]
        slowpath=df_two.loc['slowpath',0]-df_one.loc['slowpath',0]
        localHits=df_two.loc['localHits',0]-df_one.loc['localHits',0]
        #print(f"Hits: '{hits}' Miss:'{miss}' Slowpath:'{slowpath}' localHits:'{localHits}' ")
        # To calcuate slowpath to hits ratio we divide the total of slowpath by the total of all packets (hits, miss, localhits and slowpath)
        # hits_ratio=(diff of hits + Diff of local hits) / (diff of hits + diff of localHits + diff of misses + diff of slowpath)
        # slowpath_ratio= slowpath / (diff of hits + diff of localHits + diff of misses + diff of slowpath)
        '''
        From Jin:
        
        We can categorize packets into 4 groups.
        1. Go to the slowpath without asking the flow table (counter: slowpath).
        2. Look up the local cache and it is a hit (counter: hits)
        3. Look up the real flow cache and it is a hit (counter: localHits)
        4. Look up the real flow cache and it is a miss (counter: miss).

        2 and 3 are disjointed. So the number of (total) flow hits = 2 + 3.

        We can have two different hit ratios.
        a. (2+3) / (1 + 2 + 3 + 4)
        b. (2+3) / (2 + 3 + 4)
        '''
        total_events=hits+miss+slowpath+localHits
        #dict_ratios['total_events']=total_events
        slowpath_ratio=slowpath/total_events
        dict_ratios['slowpath_ratio']=slowpath_ratio
        hits_ratio=(hits+localHits)/total_events
        dict_ratios['hits_ratio']=hits_ratio
        miss_ratio=miss/total_events
        dict_ratios['miss_ratio']=miss_ratio
        hits_to_miss_ratio=(hits+localHits)/(hits+localHits+miss)
        dict_ratios['hits_to_miss_ratio']=hits_to_miss_ratio
        miss_to_hits_ratio=miss/(hits+localHits+miss)
        dict_ratios['miss_to_hits_ratio']=miss_to_hits_ratio
        #print(f"Hits Ratio={hits_ratio:.2%} Slowpath ratio={slowpath_ratio:.2%} Miss ratio={miss_ratio:.2%} Hits to Miss ratio={hits_to_miss_ratio:.2%} Miss to Hits ratio={miss_to_hits_ratio:.2%} ")

    except KeyError:
        # Handle the case where the index does not exist
        print("Error could not extract some indexes")
    return dict_ratios

def print_ratios(dict_ratios):
    # Gets a dictionary with ratios (all pct formatted) and prints it
    from prettytable import PrettyTable
    keys_list=list(dict_ratios.keys())
    table = PrettyTable(['Ratio','Value'])
    #table = PrettyTable(keys_list)
    for key, value in dict_ratios.items():
        table.add_row([key, '{:.2%}'.format(value)])
    print(table)


# Checks if input_str is json formatted and returns a dictionary if it is. Otherwise it returns an empty dictionary
def is_json(input_str):
    dict={}
    try:
        dict=json.loads(input_str)
        return dict  # Dictionary will have some data
    except json.JSONDecodeError:
        return dict  # Dictionary would be empty

def find_number(string):
    # Extracts number for a like that looks like "string1: number string2"
    import re
    pattern = r'\b\d+\b'
    match=re.search(pattern,string)
    if match:
      return int(match.group())
    else:
       return 0

# Matcher to find integers

#Testing traversing a dataframe with two indexes


prev_output1 = '''{
   "lcoreID": 0,
   "numFlows": 0,
   "numFlowsCreated": 37372,
   "hits": 1360144445,
   "miss": 3641374072,
   "slowpath": 263795196,
   "fpoHits": 0,
   "localHits": 10055472,
   "keyInsertFailCount": 0,
   "latSampleCount": 0,
   "fpoCTHwPktQueued": 0,
   "fpoCTHwPktDrop": 0,
   "fpoCTPktsInjectedToHW": 0,
   "fpoCTPktsContinuedInSW": 0,
   "fpoCTHwContextFailed": 0,
   "fpoCTHwFlowInval": 0,
   "fpoMarkMismatched": 0,
   "fpoPnicMismatched": 0,
   "fpoDelayMarkMatching": 0,
   "fpoEphemeralFlows": 0,
   "fpoTransientFlows": 0,
   "fpoBackoffTimes": 0,
   "fpoTotalBackoffFlows": 0,
   "fpoMaxBackoffFlows": 0
}'''

prev_output2 = '''{
   "lcoreID": 6,
   "numFlows": 4,
   "numFlowsCreated": 60334,
   "hits": 1301422941,
   "miss": 126439,
   "slowpath": 35697352,
   "fpoHits": 0,
   "localHits": 1554034061,
   "keyInsertFailCount": 0,
   "latSampleCount": 0,
   "fpoCTHwPktQueued": 0,
   "fpoCTHwPktDrop": 0,
   "fpoCTPktsInjectedToHW": 0,
   "fpoCTPktsContinuedInSW": 0,
   "fpoCTHwContextFailed": 0,
   "fpoCTHwFlowInval": 0,
   "fpoMarkMismatched": 0,
   "fpoPnicMismatched": 0,
   "fpoDelayMarkMatching": 0,
   "fpoEphemeralFlows": 0,
   "fpoTransientFlows": 0,
   "fpoBackoffTimes": 0,
   "fpoTotalBackoffFlows": 0,
   "fpoMaxBackoffFlows": 0
}'''


curr_output1 = '''{
   "lcoreID": 0,
   "numFlows": 0,
   "numFlowsCreated": 37372,
   "hits": 1360144445,
   "miss": 3641374078,
   "slowpath": 263798050,
   "fpoHits": 0,
   "localHits": 10055472,
   "keyInsertFailCount": 0,
   "latSampleCount": 0,
   "fpoCTHwPktQueued": 0,
   "fpoCTHwPktDrop": 0,
   "fpoCTPktsInjectedToHW": 0,
   "fpoCTPktsContinuedInSW": 0,
   "fpoCTHwContextFailed": 0,
   "fpoCTHwFlowInval": 0,
   "fpoMarkMismatched": 0,
   "fpoPnicMismatched": 0,
   "fpoDelayMarkMatching": 0,
   "fpoEphemeralFlows": 0,
   "fpoTransientFlows": 0,
   "fpoBackoffTimes": 0,
   "fpoTotalBackoffFlows": 0,
   "fpoMaxBackoffFlows": 0
}'''

curr_output2 ='''{
   "lcoreID": 6,
   "numFlows": 4,
   "numFlowsCreated": 60334,
   "hits": 1302602290,
   "miss": 126439,
   "slowpath": 35697665,
   "fpoHits": 0,
   "localHits": 1554079496,
   "keyInsertFailCount": 0,
   "latSampleCount": 0,
   "fpoCTHwPktQueued": 0,
   "fpoCTHwPktDrop": 0,
   "fpoCTPktsInjectedToHW": 0,
   "fpoCTPktsContinuedInSW": 0,
   "fpoCTHwContextFailed": 0,
   "fpoCTHwFlowInval": 0,
   "fpoMarkMismatched": 0,
   "fpoPnicMismatched": 0,
   "fpoDelayMarkMatching": 0,
   "fpoEphemeralFlows": 0,
   "fpoTransientFlows": 0,
   "fpoBackoffTimes": 0,
   "fpoTotalBackoffFlows": 0,
   "fpoMaxBackoffFlows": 0
}
'''
curr_time = int(math.floor(time.time()))
prev_time= curr_time - 10

# Create DF with current outputs Lcore 0
dict_curr_output=is_json(curr_output1)
dict_curr_output['Time']=curr_time
df_curr=pd.DataFrame.from_dict(dict_curr_output,orient='index')
df_curr=df_curr.T
df_curr.set_index(['lcoreID'], inplace=True)

dict_curr_output=is_json(curr_output2)
dict_curr_output['Time']=curr_time
df_curr2=pd.DataFrame.from_dict(dict_curr_output,orient='index')
df_curr2=df_curr2.T
df_curr2.set_index(['lcoreID'], inplace=True)
df_curr=pd.concat([df_curr,df_curr2])
print("Curr")
print(df_curr)


# Create DF with current outputs Lcore 0
dict_prev_output=is_json(prev_output1)
dict_prev_output['Time']=prev_time
df_prev=pd.DataFrame.from_dict(dict_prev_output,orient='index')
df_prev=df_prev.T
df_prev.set_index(['lcoreID'], inplace=True)

dict_prev_output=is_json(prev_output2)
dict_prev_output['Time']=prev_time
df_prev2=pd.DataFrame.from_dict(dict_prev_output,orient='index')
df_prev2=df_prev2.T
df_prev2.set_index(['lcoreID'], inplace=True)
df_prev=pd.concat([df_prev,df_prev2])
print("PREV")
print(df_prev)
diff_df=df_curr-df_prev

print("DIFF:")



non_zero_cols=diff_df.columns[diff_df.any()]
non_zero_df=diff_df[non_zero_cols].copy()
print("B4 change:")
print(non_zero_df)

grouped = non_zero_df.groupby('lcoreID')
print(grouped.get_group(6))
#non_zero_df=non_zero_df.copy()


# Apply the function to each row in non_zero_df
ratios_df = non_zero_df.apply(calculate_ratios_vectorized, axis=1)

# Print the resulting DataFrame
print("Ratios DF:")
print(ratios_df)

print("Modified non-zero:")
# Apply the function and assign results to new columns in non_zero_df
non_zero_df.loc[:, ['slowpath_ratio', 'hits_ratio', 'miss_ratio', 'hits_to_miss_ratio', 'miss_to_hits_ratio']] = non_zero_df.apply(calculate_ratios_vectorized, axis=1)

# Display the updated DataFrame
print("AFTER THE CHANGE:")
print(non_zero_df)

'''

for lcore_idx, lcore_data in non_zero_df.iterrows():
    #print("Lcore Idx :")
    #print(lcore_idx)
    #print(grouped.get_group(lcore_idx))
    dict=calculate_ratios(lcore_idx, grouped.get_group(lcore_idx))
    #print(dict)

'''
# Create DF with current outputs Lcore 6









'''
        # We now want to store the dataframe as a time series
        #print("Current Output is :")
        #print(df_curr)

        # Check if this is not the first pass
        if (prev_output == ""):
            first_output = curr_output
            prev_output = curr_output

            agg_df=df_curr
            agg_df=agg_df.T
            agg_df.set_index(['Time','lcoreID'], inplace=True)

        else:
            # Not the 1st pass let's compare the results
            prev_output = curr_output

            temp_df=df_curr
            temp_df=temp_df.T
            temp_df.set_index(['Time','lcoreID'], inplace=True)
            # Create a DF with the difference between previous and current
            agg_df=pd.concat([agg_df,temp_df])


    if (ctr != ITERATIONS):
        print("Sleeping for (seconds):" + str(DURATION))
        time.sleep(DURATION)
        #os.system('cls' if os.name == 'nt' else 'clear')
    else:
        print("Final Iteration. Calculating totals")
        print("VERY FINAL DF:")
        #print(agg_df)

    
# Accessing multi index dataframe now

# To display only non-zero columns
print("Non Zero Aggregare DF")
non_zero_cols=agg_df.columns[agg_df.any()]
non_zero_df=agg_df[non_zero_cols]
print(non_zero_df)
# Dumping to a csv file
non_zero_df.to_csv(HOSTNAME+".csv", index=True)
print("DIFF")
df_diff = non_zero_df.diff()

grouped = non_zero_df.groupby(level=0)
print("Grouped by Time")
print(grouped)

grouped = non_zero_df.groupby(level=1)
print("Grouped by Lcore")
print(grouped)
# Close the SSH connection
time.sleep(2)
ssh.close()
'''