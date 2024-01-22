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
    # For now will only do two iterations
    #parser.add_argument("-i", "--iterations", type=int, help="Number if Iterations", default=6)
    parser.add_argument("-d", "--duration", type=int, help="Duration of sleeps between iterations", default=5)

    args = parser.parse_args()
    return args

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


def get_nonzero_df(org_df):
    non_zero_cols=org_df.columns[org_df.any()]
    non_zero_df=org_df[non_zero_cols]
    return non_zero_df

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

integer_regex = r'^[+-]?\d+$'

args = validate_arguments()
HOSTNAME = args.hostname
# Example n294-esxi-ht-01.sc.sero.gic.ericsson.se
#ITERATIONS = args.iterations
ITERATIONS = 2
DURATION = args.duration

# Connect to the remote server
ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOSTNAME,
            port='22', username='root', password='N294-admin')

curr_output = ""
prev_output = ""
# Clear the screen
#os.system('cls' if os.name == 'nt' else 'clear')
# Find the lcores I want to check
COMMAND = 'esxcli network ens  lcore list'
stdin, stdout, stderr = ssh.exec_command(COMMAND)
''' Output looks like:
    Lcore ID  Switch        Affinity
--------  ------------  --------
       0  DvsPortset-2         0
       1  DvsPortset-2         0
       2  DvsPortset-2         0
       3  DvsPortset-2         0
       4  DvsPortset-2         0
       5  DvsPortset-2         0
       6  DvsPortset-2         1
       7  DvsPortset-2         1
       8  DvsPortset-2         1
       9  DvsPortset-2         1
      10  DvsPortset-2         1
      11  DvsPortset-2         1
'''
lcores_table=stdout.read().decode()
# Returns a list with all the lcores
lcores=[match.group(1) for match in re.finditer(r'\b(\d+).*', lcores_table)]


for ctr in range(1, ITERATIONS+1):
    print("Running iteration : " + str(ctr))
    curr_time = int(math.floor(time.time()))
    # Create empty dataframe
    agg_df = pd. DataFrame()

    # Execute a command on the remote server
    for lcore in lcores:
        COMMAND='nsxdp-cli ens flow-stats get -l '+lcore
        print("Command is now"+COMMAND)
        stdin, stdout, stderr = ssh.exec_command(COMMAND)
        curr_output = stdout.read().decode()
        #print(curr_output)
        dict_curr_output=is_json(curr_output)
        if dict_curr_output:
            dict_curr_output['Time']=curr_time
            df_curr=pd.DataFrame.from_dict(dict_curr_output, orient='index')
        else:
            print("Output is not JSON")
            break 

        # We now want to store the dataframe as a time series
        #print("Current Output is :")
        #print(df_curr)

        temp_df=df_curr
        temp_df=temp_df.T
        temp_df.set_index(['lcoreID'], inplace=True)
        # Create a DF with the difference between previous and current
        agg_df=pd.concat([agg_df,temp_df])


    # Running only two iterations here
    if (ctr == 1):
        first_df=agg_df
        print("First DF =")
        print(get_nonzero_df(first_df))
    if (ctr != ITERATIONS):
        print("Sleeping for (seconds):" + str(DURATION))
        time.sleep(DURATION)
        #os.system('cls' if os.name == 'nt' else 'clear')
    else:
        print("Final DF")
        second_df=agg_df
        print(get_nonzero_df(second_df))

    
# Accessing multi index dataframe now
diff_df=second_df-first_df
# To display only non-zero columns
print("Non Zero Aggregare DF")
non_zero_df=get_nonzero_df(diff_df)
print(non_zero_df)
# Dumping to a csv file
non_zero_df.to_csv(HOSTNAME+".csv", index=True)

# Close the SSH connection
time.sleep(2)
ssh.close()
